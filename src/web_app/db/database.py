from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from config import PSQL_ENGINE

async_engine = create_async_engine(PSQL_ENGINE.replace("postgresql://", "postgresql+asyncpg://"), poolclass=NullPool)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
