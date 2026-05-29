from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.notification import Notification
from app.auth.utils import hash_password
from app.db.session import get_db
from app.notifications.publisher import (
    publish_notification
)
from app.core.redis import redis_client

from app.auth.dependencies import (
    get_current_user
)

from fastapi.security import (
    OAuth2PasswordRequestForm
)

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)

from app.services.user_service import (
    create_user,
    get_user_by_email
)


from app.core.security import (
    create_refresh_token,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)

import random

from app.auth.schemas import (
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest,
    RefreshTokenRequest
)

from app.otp.publisher import (
    publish_otp_event
)
from jose import jwt, JWTError

from app.services.notification_service import create_notification


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)



@router.post(
    "/register",
    response_model=UserResponse
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = get_user_by_email(
        db,
        user_data.email
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="User already exists. Please login."
        )

    user = create_user(
        db,
        user_data
    )

    from app.services.notification_service import (
        create_notification
    )

    create_notification(
        db,
        user.id,
        "Welcome to SmartHub",
        "Your account has been created successfully."
    )

    await publish_notification({

        "email": user.email,

        "subject": "Welcome to SmartHub",

        "message": f"""
        Hi {user.email},

        Welcome to SmartHub.

        Your account has been created successfully.
        """
    })

    return user


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = get_user_by_email(
        db,
        form_data.username
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        form_data.password,
        user.hashed_password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        data={"sub": user.email}
    )

    refresh_token = create_refresh_token(
        data={"sub": user.email}
    )

    redis_client.setex(
        f"refresh:{user.email}",
        604800,
        refresh_token
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def get_me(
    current_user: User = Depends(
        get_current_user
    )
):

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name":
            current_user.full_name
    }

@router.post("/refresh")
async def refresh_access_token(
    payload: RefreshTokenRequest
):

    try:

        payload_data = jwt.decode(
            payload.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload_data.get("sub")

        if not email:

            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        stored_token = redis_client.get(
            f"refresh:{email}"
        )

        if stored_token != payload.refresh_token:

            raise HTTPException(
                status_code=401,
                detail="Refresh token invalidated"
            )

        new_access_token = create_access_token(
            data={"sub": email}
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    otp = str(random.randint(100000, 999999))
    redis_client.setex(
        f"otp:{payload.email}",
        300,
        otp
    )

    await publish_otp_event({
        "email": payload.email,
        "otp": otp,
        "retry_count": 0
    })

    return {
        "message": "OTP sent successfully"
    }

@router.post("/verify-otp")
async def verify_otp(
    payload: VerifyOtpRequest,
    db: Session = Depends(get_db)
):

    stored_otp = redis_client.get(
    f"otp:{payload.email}"
    )

    if not stored_otp:

        return {
            "message": "OTP expired or invalid"
        }

    if stored_otp != payload.otp:

        return {
            "message": "Invalid OTP"
        }

    redis_client.setex(
        f"verified:{payload.email}",
        300,
        "true"
    )

    return {
        "message": "OTP verified successfully"
    }


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    verified = redis_client.get(
        f"verified:{payload.email}"
    )

    if not verified:

        return {
            "message": "OTP verification required"
        }

    user = db.query(User).filter(
        User.email == payload.email
    ).first()

    if not user:

        return {
            "message": "User not found"
        }

    user.hashed_password = hash_password(
        payload.new_password
    )

    db.commit()

    db.refresh(user)

    redis_client.delete(
        f"otp:{payload.email}"
    )

    redis_client.delete(
        f"verified:{payload.email}"
    )

    return {
        "message": "Password reset successful"
    }

@router.post("/logout")
async def logout(
    payload: RefreshTokenRequest
):

    try:

        payload_data = jwt.decode(
            payload.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload_data.get("sub")

        if not email:

            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        redis_client.delete(
            f"refresh:{email}"
        )

        return {
            "message": "Logged out successfully"
        }

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )
    
