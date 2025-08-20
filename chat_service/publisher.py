from faststream.rabbit import RabbitBroker
from constants import AMQP_URL, EXCHANGE
from events import ChatEvent

broker = RabbitBroker(AMQP_URL)

ROUTING = {
    "new": "chat.new",
    "edit": "chat.edit",
    "delete": "chat.delete"
}

async def publish_event(ev: ChatEvent):
    rk = ROUTING[ev.type]
    await broker.publish(ev.model_dump(mode="json"), exchange=EXCHANGE, routing_key=rk)

async def publish_new(payload: dict):
    ev = ChatEvent(type="new", **payload)
    await publish_event(ev)

async def publish_edit(payload: dict):
    ev = ChatEvent(type="edit", **payload)
    await publish_event(ev)

async def publish_delete(payload: dict):
    ev = ChatEvent(type="delete", **payload)
    await publish_event(ev)
