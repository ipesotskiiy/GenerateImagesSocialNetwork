from faststream.rabbit import RabbitBroker
from constants import AMQP_URL, EXCHANGE

broker = RabbitBroker(AMQP_URL)

async def publish_new(payload: dict):
    payload.setdefault("type", "new")
    await broker.publish(payload, exchange=EXCHANGE, routing_key="chat.new")

async def publish_edit(payload: dict):
    payload["type"] = "edit"
    await broker.publish(payload, exchange=EXCHANGE, routing_key="chat.new")

async def publish_delete(payload: dict):
    payload["type"] = "delete"
    await broker.publish(payload, exchange=EXCHANGE, routing_key="chat.new")
