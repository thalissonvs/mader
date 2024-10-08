import factory
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from testcontainers.postgres import PostgresContainer

from mader.app import app
from mader.database import get_session
from mader.models import Book, Romancist, User, table_registry
from mader.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@mail.com')
    password = 'password'


class RomancistFactory(factory.Factory):
    class Meta:
        model = Romancist

    name = factory.Sequence(lambda n: f'romancist{n}')


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f'book{n}')
    year = factory.Sequence(lambda n: f'{n}')
    romancist_id = 1


@pytest_asyncio.fixture(scope='session')
async def engine():
    with PostgresContainer(driver='psycopg') as container:
        engine = create_async_engine(container.get_connection_url())
        async with engine.begin():
            yield engine


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
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


@pytest_asyncio.fixture
async def other_user(session):
    user = UserFactory()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest_asyncio.fixture
async def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json().get('access_token')


@pytest_asyncio.fixture
async def romancist(session):
    romancist_db = Romancist(name='jane austen')
    session.add(romancist_db)
    await session.commit()
    await session.refresh(romancist_db)
    return romancist_db


@pytest_asyncio.fixture
async def book(session, romancist):
    book_db = Book(
        title='pride and prejudice', year='1813', romancist_id=romancist.id
    )
    session.add(book_db)
    await session.commit()
    await session.refresh(book_db)
    return book_db
