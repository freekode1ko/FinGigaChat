"""Модуль с engine для взаимодействия с базой данных"""
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from configs.config import psql_engine

engine = create_engine(psql_engine, poolclass=NullPool)
