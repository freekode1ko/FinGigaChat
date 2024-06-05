"""Создание подключения к БД"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from configs.config import psql_engine


engine = create_engine(psql_engine, poolclass=NullPool)

async_engine = create_async_engine(str(psql_engine).replace('postgresql://', 'postgresql+asyncpg://'))

async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
