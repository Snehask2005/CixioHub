import aio_pika
import asyncio
import json

from app.notifications.constants import (
    NOTIFICATION_EXCHANGE,
    EMAIL_RETRY_QUEUE,
    ROUTING_KEY
)

RETRY_DELAY = 10


async def consume_retry_queue():

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        NOTIFICATION_EXCHANGE,
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    retry_queue = await channel.declare_queue(
        EMAIL_RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": 10000,
            "x-dead-letter-exchange": NOTIFICATION_EXCHANGE,
            "x-dead-letter-routing-key": ROUTING_KEY
        }
    )

    async with retry_queue.iterator() as queue_iter:

        async for message in queue_iter:

            async with message.process():

                data = json.loads(
                    message.body.decode()
                )

                print(
                    f"Retrying notification for {data['email']}"
                )

                await asyncio.sleep(RETRY_DELAY)

                await exchange.publish(
                    aio_pika.Message(
                        body=json.dumps(data).encode(),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    ),
                    routing_key=ROUTING_KEY
                )

                print(
                    f"Republished {data['email']} to main queue"
                )


asyncio.run(consume_retry_queue())