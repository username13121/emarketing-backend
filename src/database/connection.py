from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.models import Base

async_engine = create_async_engine(settings.DATABASE_URL_asyncpg,
                                   # echo=True
                                   )

AsyncSessionLocal = sessionmaker(bind=async_engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)