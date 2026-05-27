import aio_pika
import asyncio
import json
import random

import aiosmtplib

from email.message import EmailMessage

from app.core.config import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD
)

from app.notifications.constants import (
    NOTIFICATION_EXCHANGE,
    EMAIL_QUEUE,
    EMAIL_RETRY_QUEUE,
    EMAIL_FAILED_QUEUE,
    ROUTING_KEY
)


MAX_RETRIES = 3


async def process_notification(data):

    recipient = data["email"]

    subject = data["subject"]

    content = data["message"]

    print(
        f"Sending notification to {recipient}"
    )

    message = EmailMessage()

    message["From"] = EMAIL_ADDRESS

    message["To"] = recipient

    message["Subject"] = subject

    message.set_content(content)

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=EMAIL_ADDRESS,
        password=EMAIL_PASSWORD
    )

    print(
        "Notification sent successfully"
    )


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
        durable=True,
        arguments={
            "x-message-ttl": 10000,
            "x-dead-letter-exchange": NOTIFICATION_EXCHANGE,
            "x-dead-letter-routing-key": ROUTING_KEY
        }
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

                    retry_count = data.get(
                        "retry_count",
                        0
                    )

                    retry_count += 1

                    data["retry_count"] = retry_count

                    print(
                        f"""
                        Notification failed
                        Email: {data['email']}
                        Retry Count: {retry_count}
                        Error: {str(e)}
                        """
                    )   

                    if retry_count <= MAX_RETRIES:

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

                        print(
                            f"""
                            Notification permanently failed
                            Email: {data['email']}
                            Total Retries: {retry_count}
                            """
                        )


asyncio.run(consume())