# main_service/consumer.py
from __future__ import annotations

import logging
from typing import Any, Dict

from faststream.rabbit import RabbitBroker, RabbitMessage
from pydantic import ValidationError

from constants import AMQP_URL, EXCHANGE, CHAT_Q, DLX, DLQ
from websocket.manager import manager
from events import ChatEvent

logger = logging.getLogger(__name__)

broker = RabbitBroker(AMQP_URL)


def _to_event(body: Dict[str, Any]) -> ChatEvent:
    """
    Пытаемся распарсить событие в новый контракт ChatEvent.
    Если не получилось — пробуем «легаси» поля (message_id/new_content).
    """
    try:
        return ChatEvent.model_validate(body)
    except ValidationError:
        mapped = {
            "v": body.get("v", 1),
            "type": body.get("type"),  # "new" | "edit" | "delete"
            "id": body.get("id") or body.get("message_id"),
            "sender_id": body.get("sender_id"),
            "recipient_id": body.get("recipient_id"),
            "content": body.get("content", body.get("new_content")),
            "timestamp": body.get("timestamp"),
        }
        return ChatEvent.model_validate(mapped)


@broker.subscriber(CHAT_Q, exchange=EXCHANGE)
async def on_message(body: dict, msg: RabbitMessage):
    """
    Основной обработчик событий из RabbitMQ.
    Валидируем событие и шлём его обоим участникам диалога по WebSocket.
    """
    try:
        ev = _to_event(body)

        targets = [ev.sender_id, ev.recipient_id]

        if ev.type == "new":
            await manager.send_many(
                targets,
                {"type": "new", "message": ev.model_dump(mode="json")},
            )

        elif ev.type == "edit":
            await manager.send_many(
                targets,
                {
                    "type": "edit",
                    "message_id": ev.id,
                    "new_content": ev.content,
                },
            )

        elif ev.type == "delete":
            await manager.send_many(
                targets,
                {"type": "delete", "message_id": ev.id},
            )

        else:
            logger.error("Unknown event type: %r; body=%r", ev.type, body)
            await msg.reject(requeue=False)

    except ValidationError as e:
        logger.exception("Event validation failed: %s; body=%r", e, body)
        await msg.reject(requeue=False)  # уйдёт в DLQ
    except Exception:
        logger.exception("Unhandled error while processing message: %r", body)
        await msg.reject(requeue=False)


@broker.subscriber(DLQ, exchange=DLX)
async def on_dead(body: dict):
    logger.error("[DLQ] dead-lettered: %r", body)


async def start_consumer():
    await broker.connect()
    await broker.start()
