from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from api_acess_alterdata.settings import Settings

setting = Settings()

engine = create_async_engine(setting.DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
