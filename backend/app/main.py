import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.core.database import lifespan

app = FastAPI(lifespan=lifespan)
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the API!"}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
