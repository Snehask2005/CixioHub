from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str
):

    notification = Notification(
        user_id=user_id,
        title=title,
        message=message
    )

    db.add(notification)

    db.commit()

    db.refresh(notification)

    return notification