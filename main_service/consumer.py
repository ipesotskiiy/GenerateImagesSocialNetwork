from faststream.rabbit import RabbitBroker
from websocket.manager import manager

broker = RabbitBroker("amqp://guest:guest@localhost/")

@broker.subscriber("chat_messages")
async def on_message(body: dict):
    print("[CONSUME] from RMQ:", body)
    t = body.get("type")
    if t == "new":
        await manager.send_many([body["sender_id"], body["recipient_id"]],
                                {"type": "new", "message": body})
    elif t == "edit":
        await manager.send_many([body["sender_id"], body["recipient_id"]],
                                {"type": "edit",
                                 "message_id": body["message_id"],
                                 "new_content": body["new_content"]})
    elif t == "delete":
        await manager.send_many([body["sender_id"], body["recipient_id"]],
                                {"type": "delete", "message_id": body["message_id"]})

async def start_consumer():
    await broker.connect()
    await broker.start()
