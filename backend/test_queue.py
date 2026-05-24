from app.queue.producer import send_message
import asyncio

message = {
    "email": "test@gmail.com",
    "message": "Welcome to CixioHub"
}

asyncio.run(send_message(message))