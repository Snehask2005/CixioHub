import aio_pika
import asyncio
import json
import random

from app.notifications.constants import (
    NOTIFICATION_EXCHANGE,
    EMAIL_QUEUE,
    EMAIL_RETRY_QUEUE,
    EMAIL_FAILED_QUEUE,
    ROUTING_KEY
)


MAX_RETRIES = 3


async def process_notification(data):

    print(f"Processing notification for {data['email']}")

    failure = random.choice([True, False])

    if failure:
        raise Exception("Simulated notification failure")

    print("Notification sent successfully")


async def consume():

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        NOTIFICATION_EXCHANGE,
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    queue = await channel.declare_queue(
        EMAIL_QUEUE,
        durable=True
    )

    retry_queue = await channel.declare_queue(
    EMAIL_RETRY_QUEUE,
    durable=True
    )   

    failed_queue = await channel.declare_queue(
    EMAIL_FAILED_QUEUE,
    durable=True
    )

    await queue.bind(
        exchange,
        routing_key=ROUTING_KEY
    )
    await retry_queue.bind(
    exchange,
    routing_key="email.retry"
    )

    await failed_queue.bind(
    exchange,
    routing_key="email.failed"
    )

    async with queue.iterator() as queue_iter:

        async for message in queue_iter:

            async with message.process():

                data = json.loads(
                    message.body.decode()
                )

                try:

                    await process_notification(data)

                except Exception as e:

                    print("FAILED:", str(e))

                    retry_count = data.get(
                        "retry_count",
                        0
                    )

                    data["retry_count"] = retry_count + 1

                    if retry_count < MAX_RETRIES:

                        await exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(data).encode(),
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                            ),
                            routing_key="email.retry"
                        )

                    else:

                        await exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(data).encode(),
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                            ),
                            routing_key="email.failed"
                        )

                        print("Moved to failed queue")


asyncio.run(consume())