import aio_pika
import json

from app.otp.constants import (
    OTP_EXCHANGE,
    OTP_ROUTING_KEY
)


async def publish_otp_event(data):

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        OTP_EXCHANGE,
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    await exchange.publish(
        aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key=OTP_ROUTING_KEY
    )

    await connection.close()