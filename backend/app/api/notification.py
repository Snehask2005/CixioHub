from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.notification import Notification
from app.models.user import User


from app.auth.dependencies import (
    get_current_user
)

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.get("/")
async def get_notifications(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    notifications = (
        db.query(Notification)
        .filter(
            Notification.user_id ==
            current_user.id
        )
        .all()
    )

    return notifications

@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id
        )
        .first()
    )

    if not notification:

        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    notification.is_read = True

    db.commit()

    return {
        "message": "Notification marked as read"
    }

@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):

    count = (
        db.query(Notification)
        .filter(
            Notification.user_id ==
            current_user.id,

            Notification.is_read == False
        )
        .count()
    )

    return {
        "count": count
    }