import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from mader.app import app
from mader.database import get_session
from mader.models import table_registry


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
