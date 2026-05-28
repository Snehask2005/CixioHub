from pydantic import BaseModel


class ForgotPasswordRequest(BaseModel):
    email: str


class VerifyOtpRequest(BaseModel):
    email: str
    otp: str


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str

class RefreshTokenRequest(
    BaseModel
):

    refresh_token: str