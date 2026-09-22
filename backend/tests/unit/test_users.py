import pytest

from app.users import service as user_service
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate


class TestCreateUserService:
    async def test_create_user_success(self, db_session):
        user_in = UserCreate(username="testuser", password="testpassword")
        user = await user_service.create_user(db_session, user_in)

        assert isinstance(user, User)
        assert user.username == user_in.username
        assert user.id is not None

    async def test_create_user_existing_username(self, db_session):
        user_in = UserCreate(username="testuser", password="testpassword")
        db_session.add(User(username=user_in.username, hashed_password="hashedpassword"))
        await db_session.commit()

        with pytest.raises(user_service.ExistingUser):
            await user_service.create_user(db_session, user_in)

class TestReadUserService:
    async def test_get_user_by_id_success(self, db_session):
        user_in = UserCreate(username="testuser", password="testpassword")
        created_user = await user_service.create_user(db_session, user_in)

        fetched_user = await user_service.get_user_by_id(db_session, created_user.id)

        assert fetched_user.id == created_user.id
        assert fetched_user.username == created_user.username

    async def test_get_user_by_id_not_found(self, db_session):
        with pytest.raises(user_service.UserNotFound):
            await user_service.get_user_by_id(db_session, 9999)

    async def test_get_user_by_username_success(self, db_session):
        user_in = UserCreate(username="testuser", password="testpassword")
        created_user = await user_service.create_user(db_session, user_in)

        fetched_user = await user_service.get_user_by_username(db_session, created_user.username)

        assert fetched_user.id == created_user.id
        assert fetched_user.username == created_user.username

    async def test_get_user_by_username_not_found(self, db_session):
        with pytest.raises(user_service.UserNotFound):
            await user_service.get_user_by_username(db_session, "nonexistentuser")

    async def test_get_all_users(self, db_session):
        user_in1 = UserCreate(username="testuser1", password="testpassword1")
        user_in2 = UserCreate(username="testuser2", password="testpassword2")

        await user_service.create_user(db_session, user_in1)
        await user_service.create_user(db_session, user_in2)

        users = await user_service.get_all_users(db_session)

        assert len(users) == 2
        assert any(user.username == "testuser1" for user in users)
        assert any(user.username == "testuser2" for user in users)

class TestUpdateUserService:
    async def test_update_user_success(self, db_session):
        user_in = UserCreate(username="testuser", password="testpassword")
        user = await user_service.create_user(db_session, user_in)

        update_data = UserUpdate(username="updateduser")
        updated_user = await user_service.update_user(db_session, user, user_update=update_data)

        assert updated_user.username == update_data.username

    async def test_update_user_existing_username(self, db_session):
        user_in1 = UserCreate(username="testuser1", password="testpassword1")
        user_in2 = UserCreate(username="testuser2", password="testpassword2")

        user1 = await user_service.create_user(db_session, user_in1)
        await user_service.create_user(db_session, user_in2)

        with pytest.raises(user_service.ExistingUser):
            await user_service.update_user(db_session, user1, user_update=UserUpdate(username="testuser2"))

class TestDeleteUserService:
    async def test_delete_user(self, db_session):
        user_in = UserCreate(username="testuser", password="testpassword")
        user = await user_service.create_user(db_session, user_in)

        await user_service.delete_user(db_session, user)

        with pytest.raises(user_service.UserNotFound):
            await user_service.get_user_by_id(db_session, user.id)

        with pytest.raises(user_service.UserNotFound):
            await user_service.get_user_by_username(db_session, user.username)
