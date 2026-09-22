import uvicorn
from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.database import lifespan
from app.core.exceptions import init_exception_handlers
from app.users.router import router as users_router

app = FastAPI(lifespan=lifespan)
app.include_router(users_router)
app.include_router(auth_router)
init_exception_handlers(app)
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the API!"}

if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
