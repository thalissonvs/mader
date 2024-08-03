from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from mader.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


def get_session():
    with AsyncSession(engine) as session:
        yield session
