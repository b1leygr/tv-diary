from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import AuthenticationError
from app.auth.schemas import Token
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.users import service as user_service
from app.users.exceptions import UserNotFound
from app.users.models import User


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Token:
    try:
        user = await user_service.get_user_by_username(db, username)
    except UserNotFound:
        _ = verify_password(password, settings.DUMMY_HASH)
        raise AuthenticationError()

    valid, updated_hash = verify_password(password, user.hashed_password)
    if not valid:
        raise AuthenticationError()
    if updated_hash:
        await update_user_hash(db, user, updated_hash)
    access_token = create_access_token(sub=user.id)
    return Token(access_token=access_token, token_type='bearer')


async def update_user_hash(db: AsyncSession, user: User, new_hash: str) -> None:
    user.hashed_password = new_hash
    db.add(user)
    await db.commit()
    await db.refresh(user)
