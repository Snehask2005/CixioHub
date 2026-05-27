from fastapi import FastAPI

from app.db.database import (
    Base,
    engine
)


from app.api.auth import router as auth_router


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to CixioHub!"}



Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

