import aio_pika
import asyncio
import json
import random
import aiosmtplib

from app.otp.constants import (
    OTP_EXCHANGE,
    OTP_QUEUE,
    OTP_RETRY_QUEUE,
    OTP_FAILED_QUEUE,
    OTP_ROUTING_KEY
)

from email.message import EmailMessage

from app.core.config import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD
)

MAX_RETRIES = 3


async def process_otp(data):

    recipient = data["email"]

    otp = data["otp"]

    print(
        f"Sending OTP {otp} to {recipient}"
    )

    message = EmailMessage()

    message["From"] = EMAIL_ADDRESS
    message["To"] = recipient
    message["Subject"] = "SmartHub Password Reset OTP"

    message.set_content(
        f"""
        Your SmartHub OTP is:

        {otp}

        This OTP will expire in 5 minutes.
        """
    )

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=EMAIL_ADDRESS,
        password=EMAIL_PASSWORD
    )

    print("OTP sent successfully")

async def consume():

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        OTP_EXCHANGE,
        aio_pika.ExchangeType.DIRECT,
        durable=True
    )

    queue = await channel.declare_queue(
        OTP_QUEUE,
        durable=True
    )

    retry_queue = await channel.declare_queue(
        OTP_RETRY_QUEUE,
        durable=True,
        arguments={
            "x-message-ttl": 10000,
            "x-dead-letter-exchange": OTP_EXCHANGE,
            "x-dead-letter-routing-key": OTP_ROUTING_KEY
        }
    )

    failed_queue = await channel.declare_queue(
        OTP_FAILED_QUEUE,
        durable=True
    )

    await queue.bind(
        exchange,
        routing_key=OTP_ROUTING_KEY
    )

    await retry_queue.bind(
        exchange,
        routing_key="otp.retry"
    )

    await failed_queue.bind(
        exchange,
        routing_key="otp.failed"
    )

    async with queue.iterator() as queue_iter:

        async for message in queue_iter:

            async with message.process():

                data = json.loads(
                    message.body.decode()
                )

                try:

                    await process_otp(data)

                except Exception as e:

                    retry_count = data.get(
                        "retry_count",
                        0
                    )

                    retry_count += 1

                    data["retry_count"] = retry_count

                    print(
                        f"""
                        OTP sending failed
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
                            routing_key="otp.retry"
                        )

                    else:

                        await exchange.publish(
                            aio_pika.Message(
                                body=json.dumps(data).encode(),
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                            ),
                            routing_key="otp.failed"
                        )

                        print(
                            f"""
                            OTP permanently failed
                            Email: {data['email']}
                            """
                        )


asyncio.run(consume())