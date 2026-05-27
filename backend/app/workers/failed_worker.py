import aio_pika
import asyncio
import json

from app.notifications.constants import (
    EMAIL_FAILED_QUEUE
)


async def inspect_failed_queue():

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    failed_queue = await channel.declare_queue(
        EMAIL_FAILED_QUEUE,
        durable=True
    )

    print("Inspecting failed queue...\n")

    async with failed_queue.iterator() as queue_iter:

        async for message in queue_iter:

            async with message.process():

                data = json.loads(
                    message.body.decode()
                )

                print(
                    f"""
                    FAILED NOTIFICATION
                    -------------------
                    Email: {data['email']}
                    Subject: {data['subject']}
                    Retry Count: {data['retry_count']}
                    """
                )


asyncio.run(inspect_failed_queue())