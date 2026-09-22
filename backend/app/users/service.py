from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.users.exceptions import ExistingUser, UserNotFound
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    user = User(username=user_in.username, hashed_password=get_password_hash(user_in.password))
    db.add(user)

    try:
        await db.commit()
    except IntegrityError as e:
        await db.rollback()
        raise ExistingUser(username=user_in.username) from e

    await db.refresh(user)
    return user

async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise UserNotFound(user_id=user_id)

    return user

async def get_user_by_username(db: AsyncSession, username: str) -> User:
        query = select(User).where(User.username == username)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise UserNotFound(username=username)

        return user

async def get_all_users(db: AsyncSession) -> list[User]:
        query = select(User)
        result = await db.execute(query)
        users = result.scalars().all()

        if not users:
            raise UserNotFound()

        return list(users)

async def update_user(db: AsyncSession, user: User, user_update: UserUpdate) -> User:
        try:
            update_data = user_update.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(user, field, value)

            await db.commit()
            await db.refresh(user)
            return user

        except IntegrityError as e:
            await db.rollback()
            raise ExistingUser(username=user_update.username) from e

async def delete_user(db: AsyncSession, user: User) -> None:
        await db.delete(user)
        await db.commit()
