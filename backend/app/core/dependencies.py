from collections.abc import AsyncGenerator
from typing import Annotated

import httpx2
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidCredentials
from app.core.config import settings
from app.core.database import get_db
from app.core.security import parse_jwt_token
from app.users import service as user_service
from app.users.models import User

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[dict, Depends(parse_jwt_token)], db: DbSession
) -> User:
    user_id = token.get('sub')
    if not user_id:
        raise InvalidCredentials()

    user = await user_service.get_user_by_id(db, int(user_id))
    if not user:
        raise InvalidCredentials()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def tmdb_client() -> AsyncGenerator[httpx2.AsyncClient]:
    async with httpx2.AsyncClient(
        base_url='https://api.themoviedb.org/3',
        headers={
            'Accept': 'application/json',
            'Authorization': f'Bearer {settings.TMDB_AUTH}',
        },
    ) as client:
        yield client


TmdbClient = Annotated[httpx2.AsyncClient, Depends(tmdb_client)]
