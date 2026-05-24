from fastapi import FastAPI
from app.api.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "CixioHub Backend Running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }