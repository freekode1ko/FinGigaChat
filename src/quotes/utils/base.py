"""Модуль для сохранения даты последней сборки котировок"""
from datetime import datetime

import pandas as pd

from db.database import engine


def read_curdatetime() -> datetime:
    """
    Чтение даты последней сборки из базы данных

    return Дата последней сборки
    """
    curdatetime = pd.read_sql_query('SELECT * FROM "date_of_last_build"', con=engine)
    return curdatetime['date_time'][0]
