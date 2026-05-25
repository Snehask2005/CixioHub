from app.notifications.publisher import (
    publish_notification
)

import asyncio


async def main():

    for i in range(50):

        message = {
            "user_id": str(i),
            "email": f"user{i}@test.com",
            "subject": "Bulk Notification",
            "message": f"Notification {i}",
            "retry_count": 0
        }

        await publish_notification(message)

        print(f"Published {i}")


asyncio.run(main())