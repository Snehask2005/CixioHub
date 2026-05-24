from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


def create_user(
    db: Session,
    user_data: UserCreate
):

    hashed_pw = hash_password(user_data.password)

    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_pw
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_email(
    db: Session,
    email: str
):

    return db.query(User).filter(
        User.email == email
    ).first()