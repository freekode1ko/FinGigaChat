"""Модуль для создания движка SQLAlchemy для подключения к базе данных PostgreSQL."""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool

from configs.config import psql_engine

# Создание движка SQLAlchemy для подключения к базе данных PostgreSQL с использованием NullPool
engine = create_engine(psql_engine, poolclass=NullPool)

async_engine = create_async_engine(psql_engine.replace("postgresql://", "postgresql+asyncpg://"), poolclass=NullPool)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
