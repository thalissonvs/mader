import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from mader.app import app
from mader.database import get_session
from mader.models import User, table_registry
from mader.security import get_password_hash


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session):
    async def get_test_session():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_test_session
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session):
    password = 'password'
    user_db = User(
        username='test',
        password=get_password_hash(password),
        email='test@test.com',
    )

    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)

    user_db.clean_password = password  # monkey patching

    return user_db
