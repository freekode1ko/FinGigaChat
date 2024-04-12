from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from config import PSQL_ENGINE

engine = create_engine(PSQL_ENGINE, poolclass=NullPool)
