from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from mader.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():  # pragma: no cover
    async with AsyncSession(engine) as session:
        yield session
