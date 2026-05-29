from fastapi import FastAPI

from app.db.database import (
    Base,
    engine
)


from app.api.auth import router as auth_router
from app.api.notification import router as notification_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to CixioHub!"}



Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(
    notification_router
)

