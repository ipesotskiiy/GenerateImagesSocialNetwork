from faststream.rabbit import RabbitBroker

broker = RabbitBroker("amqp://guest:guest@localhost/")


async def start_consumer():
    await broker.connect()