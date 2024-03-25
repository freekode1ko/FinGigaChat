from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import declarative_base

from configs.config import psql_engine

engine = create_engine(psql_engine, poolclass=NullPool)

Base = declarative_base()
metadata = Base.metadata
