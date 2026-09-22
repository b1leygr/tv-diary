from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(name="db_session", scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        async def override_get_db() -> AsyncGenerator[AsyncSession]:
            yield session

        app.dependency_overrides[get_db] = override_get_db
        yield session

        app.dependency_overrides.pop(get_db, None)

    await engine.dispose()
