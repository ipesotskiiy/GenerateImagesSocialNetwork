from faststream.rabbit import RabbitBroker, RabbitMessage
from constants import AMQP_URL, EXCHANGE, CHAT_Q, DLX, DLQ
from websocket.manager import manager

broker = RabbitBroker(AMQP_URL)

@broker.subscriber(CHAT_Q, exchange=EXCHANGE)   # ← без routing_key
async def on_message(body: dict, msg: RabbitMessage):
    try:
        t = body.get("type")
        if t == "new":
            await manager.send_many(
                [body["sender_id"], body["recipient_id"]],
                {"type": "new", "message": body},
            )
        elif t == "edit":
            await manager.send_many(
                [body["sender_id"], body["recipient_id"]],
                {"type": "edit",
                 "message_id": body["message_id"],
                 "new_content": body["new_content"]},
            )
        elif t == "delete":
            await manager.send_many(
                [body["sender_id"], body["recipient_id"]],
                {"type": "delete", "message_id": body["message_id"]},
            )
    except Exception:
        await msg.reject(requeue=False)  # в DLQ

@broker.subscriber(DLQ, exchange=DLX)          # ← без routing_key
async def on_dead(body: dict):
    print("[DLQ] dead-lettered:", body)

async def start_consumer():
    await broker.connect()
    await broker.start()
