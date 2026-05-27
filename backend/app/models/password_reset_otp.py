from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime
)

from datetime import datetime, timedelta

from app.db.database import Base


class PasswordResetOTP(Base):

    __tablename__ = "password_reset_otps"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String,
        nullable=False
    )

    otp = Column(
        String,
        nullable=False
    )

    is_verified = Column(
        Boolean,
        default=False
    )

    created_at = Column(
    DateTime,
    default=datetime.now
    )