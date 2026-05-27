import asyncio

from app.otp.publisher import (
    publish_otp_event
)


async def main():

    data = {
    "email": "rishitmenon@gmail.com",
    "otp": "482913",
    "retry_count": 0
    }

    await publish_otp_event(data)

    print("OTP event published")


asyncio.run(main())