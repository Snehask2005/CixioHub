import aio_pika
import json

from app.notifications.constants import (
    NOTIFICATION_EXCHANGE,
    ROUTING_KEY
)


async def publish_notification(message: dict):

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        NOTIFICATION_EXCHANGE,
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key=ROUTING_KEY
    )

    await connection.close()