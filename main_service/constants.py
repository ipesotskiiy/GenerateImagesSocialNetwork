from faststream.rabbit import RabbitQueue, RabbitExchange, ExchangeType

AMQP_URL = "amqp://guest:guest@localhost/"

EXCHANGE = RabbitExchange("chat.events", type=ExchangeType.DIRECT, durable=True)
DLX      = RabbitExchange("chat.dlx",    type=ExchangeType.DIRECT, durable=True)

CHAT_Q = RabbitQueue(
    "chat_messages",
    durable=True,
    auto_delete=False,
    routing_key="chat.new",  # ← ключ биндинга для основной очереди
    arguments={
        "x-dead-letter-exchange": DLX.name,
        "x-dead-letter-routing-key": "chat.dead",
    },
)

DLQ = RabbitQueue(
    "chat_messages.dlq",
    durable=True,
    auto_delete=False,
    routing_key="chat.dead",  # ← ключ биндинга для DLQ
)
