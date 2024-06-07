"""Модуль для создания движка SQLAlchemy для подключения к базе данных PostgreSQL."""
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from configs.config import psql_engine

# Создание движка SQLAlchemy для подключения к базе данных PostgreSQL с использованием NullPool
engine = create_engine(psql_engine, poolclass=NullPool)
