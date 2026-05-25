from pydantic import BaseModel
from typing import Optional


class NotificationMessage(BaseModel):

    user_id: str

    email: str

    subject: str

    message: str

    retry_count: int = 0