from collections.abc import AsyncGenerator

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from alembic import command
from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.main import app
from app.users.models import User


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    alembic_cfg = Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', settings.DATABASE_URL)
    command.upgrade(alembic_cfg, 'head')
    yield
    command.downgrade(alembic_cfg, 'base')


@pytest.fixture(scope='session')
async def test_engine():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope='function')
async def db_session(test_engine) -> AsyncGenerator[AsyncSession]:
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        AsyncSessionLocal = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode='create_savepoint',
        )

        async with AsyncSessionLocal() as session:

            async def override_get_db() -> AsyncGenerator[AsyncSession]:
                yield session

            app.dependency_overrides[get_db] = override_get_db

            yield session

            app.dependency_overrides.pop(get_db, None)

        await transaction.rollback()


@pytest.fixture(name='client', scope='function')
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        yield client


@pytest.fixture(name='test_user', scope='function')
def test_user() -> User:
    return User(username='testuser', hashed_password='testpassword')


@pytest.fixture(name='override_get_current_user', scope='function')
def override_get_current_user_fixture(test_user: User):
    async def override_get_current_user() -> User:
        return test_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)
