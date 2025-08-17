from faststream.rabbit import RabbitBroker

AMQP_URL = "amqp://guest:guest@localhost/"
broker = RabbitBroker(AMQP_URL)

async def publish_new(payload: dict):
    print("[PUBLISH] new -> chat_messages:", payload)
    await broker.publish(payload, "chat_messages")

async def publish_edit(payload: dict):
    print("[PUBLISH] edit -> chat_messages:", payload)
    await broker.publish(payload, "chat_messages")

async def publish_delete(payload: dict):
    print("[PUBLISH] delete -> chat_messages:", payload)
    await broker.publish(payload, "chat_messages")

