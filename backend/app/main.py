from fastapi import FastAPI

from app.db.database import (
    Base,
    engine
)

from app.models.password_reset_otp import (
    PasswordResetOTP
)

from app.api.auth import router as auth_router


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)