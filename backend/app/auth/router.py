from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import service as auth_service
from app.auth.schemas import Token
from app.core.dependencies import DbSession

router = APIRouter(
    prefix='/sessions',
    tags=['auth']
)

@router.post('')
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession) -> Token:
    return await auth_service.authenticate_user(db, form_data.username, form_data.password)
