from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.auth.utils import hash_password
from datetime import datetime, timedelta
from fastapi import Depends

from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.password_reset_otp import (
    PasswordResetOTP
)

from app.db.database import get_db

from app.models.password_reset_otp import (
    PasswordResetOTP
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

from app.db.session import get_db

from app.core.security import (
    verify_password,
    create_access_token
)

import random

from app.auth.schemas import (
    ForgotPasswordRequest,
    VerifyOtpRequest,
    ResetPasswordRequest
)



from app.otp.publisher import (
    publish_otp_event
)



router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
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
            detail="Email already registered"
        )

    return create_user(db, user_data)


@router.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):

    user = get_user_by_email(
        db,
        user_data.email
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    if not verify_password(
        user_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        data={"sub": user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    db.query(
        PasswordResetOTP
    ).filter(
        PasswordResetOTP.email == payload.email
    ).delete()

    db.commit()

    otp = str(
        random.randint(100000, 999999)
    )

    otp_entry = PasswordResetOTP(
        email=payload.email,
        otp=otp
    )

    db.add(otp_entry)

    db.commit()

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

    otp_entry = db.query(
        PasswordResetOTP
    ).filter(
        PasswordResetOTP.email == payload.email,
        PasswordResetOTP.otp == payload.otp
    ).first()

    if not otp_entry:

        return {
            "message": "Invalid OTP"
        }
    if datetime.utcnow() - otp_entry.created_at > timedelta(minutes=5):

        return {
            "message": "OTP expired"
        }


    otp_entry.is_verified = True

    db.commit()

    return {
        "message": "OTP verified successfully"
    }


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    otp_entry = db.query(
        PasswordResetOTP
    ).filter(
        PasswordResetOTP.email == payload.email,
        PasswordResetOTP.is_verified == True
    ).first()

    if not otp_entry:

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
    db.delete(otp_entry)
    db.commit()

    return {
        "message": "Password reset successful"
    }