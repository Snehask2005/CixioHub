import uuid

from sqlalchemy import (
    Column,
    String,
    Boolean,
    ForeignKey
)

from app.db.database import Base


class Notification(Base):

    __tablename__ = "notifications"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(
        String,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    is_read = Column(
        Boolean,
        default=False
    )