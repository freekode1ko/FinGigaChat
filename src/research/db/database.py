from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from configs.config import psql_engine


engine = create_engine(psql_engine, poolclass=NullPool)

async_engine = create_async_engine(str(psql_engine).replace("postgresql://", "postgresql+asyncpg://"))

async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
