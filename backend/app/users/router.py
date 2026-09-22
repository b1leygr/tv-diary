from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from app.core.dependencies import CurrentUser, DbSession
from app.users import service as user_service
from app.users.models import User
from app.users.schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.post('', response_model=UserResponse)
async def create_user(user_data: UserCreate, db: DbSession) -> User:
    return await user_service.create_user(db, user_data)

@router.get('/me', response_model=UserResponse)
async def get_current_user(current_user: CurrentUser) -> User:
    return current_user

@router.get('', response_model=UserResponse | list[UserResponse])
async def get_users(*, username: Annotated[str | None, Query(description='A username or no argument for all users')] = None, db: DbSession) -> User | list[User]:
    if username:
        return await user_service.get_user_by_username(db, username)
    else:
        return await user_service.get_all_users(db)

@router.get('/{user_id}', response_model=UserResponse)
async def get_user_by_id(user_id: Annotated[int, Path(description='A user ID')], db: DbSession) -> User:
    return await user_service.get_user_by_id(db, user_id)

@router.put('/me', response_model=UserResponse)
async def update_current_user(user_update: UserUpdate, current_user: CurrentUser, db: DbSession) -> User:
    return await user_service.update_user(db, current_user, user_update=user_update)

@router.delete('/me', status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(current_user: CurrentUser, db: DbSession) -> None:
    return await user_service.delete_user(db, current_user)
