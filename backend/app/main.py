from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.database import lifespan
from app.core.exceptions import init_exception_handlers
from app.tv.router import router as shows_router
from app.users.router import router as users_router

app = FastAPI(lifespan=lifespan, generate_unique_id_function=lambda route: route.name)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(shows_router)
init_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', tags=['Root'])
async def root():
    return {'message': "Welcome to the API!"}
