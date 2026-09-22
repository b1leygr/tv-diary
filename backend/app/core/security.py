from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.auth.exceptions import InvalidCredentials
from app.core.config import settings

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/sessions', auto_error=False)


def create_access_token(sub: str | Any) -> str:
    expire = datetime.now(UTC) + timedelta(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {'sub': str(sub), 'exp': expire}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def parse_jwt_token(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    if not token:
        raise InvalidCredentials()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return payload
    except jwt.PyJWTError:
        raise InvalidCredentials()


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    return password_hash.verify_and_update(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)
