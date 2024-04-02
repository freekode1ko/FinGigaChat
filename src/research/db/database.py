from configs.config import psql_engine
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

engine = create_engine(psql_engine, poolclass=NullPool)
