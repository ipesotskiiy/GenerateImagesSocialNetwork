from faststream.rabbit import RabbitBroker

from constants import AMQP_URL

broker = RabbitBroker(AMQP_URL)


async def start_consumer():
    await broker.connect()