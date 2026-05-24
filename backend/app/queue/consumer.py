import aio_pika
import asyncio

async def consume():

    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost/"
    )

    channel = await connection.channel()

    queue = await channel.declare_queue(
        "email.process",
        durable=True
    )

    async with queue.iterator() as queue_iter:

        async for message in queue_iter:

            async with message.process():

                print("Received:", message.body.decode())

asyncio.run(consume())