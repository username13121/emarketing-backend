from sqlalchemy.ext.asyncio import AsyncSession
from .connection import AsyncSessionLocal


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as db_session:
        yield db_session
