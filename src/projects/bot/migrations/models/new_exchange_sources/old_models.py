"""Старые таблицы с курсами"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base


Base = declarative_base()
metadata = Base.metadata


t_exc = sa.Table(
    'exc', metadata,
    sa.Column('Валюта', sa.Text),
    sa.Column('Курс', sa.DOUBLE_PRECISION(precision=53))
)
