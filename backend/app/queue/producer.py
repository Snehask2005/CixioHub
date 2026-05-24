import aio_pika
import asyncio
import json

async def send_message(message: dict):

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    queue = await channel.declare_queue(
        "email.process",
        durable=True
    )

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key=queue.name
    )

    await connection.close()