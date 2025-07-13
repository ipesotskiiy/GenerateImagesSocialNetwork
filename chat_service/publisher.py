from faststream.rabbit import RabbitBroker
import asyncio

broker = RabbitBroker("amqp://guest:guest@localhost/")

async def main():
    await broker.connect()
    await broker.publish(
        {"sender_id": 123, "recipient_id": 555, "content": "Привет, RabbitMQ"},
        "chat_messages"
    )
    print("Сообщение отправлено!")
    await broker.close()

if __name__ == "__main__":
    asyncio.run(main())
