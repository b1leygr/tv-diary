import pytest

from app.users.schemas import UserCreate


class TestCreateUserRoute:
    async def test_create_user_success(self, client):
        user_in = UserCreate(username="testuser", password="testpassword")
        response = await client.post("/users", json=user_in.model_dump())

        assert response.status_code == 200
        assert response.json()["username"] == user_in.username

    async def test_create_user_already_exists(self, client):
        user_in = UserCreate(username="testuser", password="testpassword")
        await client.post("/users", json=user_in.model_dump())

        response = await client.post("/users", json=user_in.model_dump())

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]


class TestReadUserRoute:
    async def test_get_user_by_username_success(self, client):
        user_in = UserCreate(username="testuser", password="testpassword")
        await client.post("/users", json=user_in.model_dump())

        response = await client.get(f"/users?username={user_in.username}")

        assert response.status_code == 200
        assert response.json()["username"] == user_in.username

    async def test_get_user_by_username_not_found(self, client):
        response = await client.get("/users?username=nonexistentuser")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_get_user_by_id_success(self, client):
        user_in = UserCreate(username="testuser", password="testpassword")
        response_create = await client.post("/users", json=user_in.model_dump())
        user_id = response_create.json()["id"]

        response = await client.get(f"/users/{user_id}")

        assert response.status_code == 200
        assert response.json()["username"] == user_in.username

    async def test_get_user_by_id_not_found(self, client):
        response = await client.get("/users/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestReadCurrentUserRoute:
    @pytest.mark.usefixtures("override_get_current_user")
    async def test_get_current_user_success(self, db_session, client, test_user):
        db_session.add(test_user)
        await db_session.flush()

        response = await client.get("/users/me")

        assert response.status_code == 200
        assert response.json()["username"] == test_user.username

    async def test_get_current_user_unauthorized(self, client):
        response = await client.get("/users/me")

        assert response.status_code == 401
        assert "Could not validate" in response.json()["detail"]


class TestUpdateCurrentUserRoute:
    @pytest.mark.usefixtures("override_get_current_user")
    async def test_update_current_user_success(self, db_session, client, test_user):
        db_session.add(test_user)
        await db_session.flush()

        new_username = "updateduser"
        response = await client.put("/users/me", json={"username": new_username})

        assert response.status_code == 200
        assert response.json()["username"] == new_username

    @pytest.mark.usefixtures("override_get_current_user")
    async def test_update_current_user_existing_username(self, db_session, client, test_user):
        db_session.add(test_user)
        await db_session.flush()

        existing_user = UserCreate(username="anotheruser", password="anotherpassword")
        await client.post("/users", json=existing_user.model_dump())

        response = await client.put("/users/me", json={"username": existing_user.username})

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    async def test_update_current_user_unauthorized(self, client):
        response = await client.put("/users/me", json={"username": "updateduser"})

        assert response.status_code == 401
        assert "Could not validate" in response.json()["detail"]


class TestDeleteCurrentUserRoute:
    @pytest.mark.usefixtures("override_get_current_user")
    async def test_delete_current_user_success(self, db_session, client, test_user):
        db_session.add(test_user)
        await db_session.flush()

        response = await client.delete("/users/me")

        assert response.status_code == 204

        deleted_user = await db_session.get(type(test_user), test_user.id)
        assert deleted_user is None

    async def test_delete_current_user_unauthorized(self, client):
        response = await client.delete("/users/me")

        assert response.status_code == 401
        assert "Could not validate" in response.json()["detail"]
