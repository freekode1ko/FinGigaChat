"""Интерфейс для взаимодействия с таблицами источниками для парсинга"""
# flake8:noqa
import pandas as pd

from db import database
from log.logger_base import logger

__table_name__ = 'parser_source'


def get_parser_data_for_create() -> pd.DataFrame:
    """Вынимает из бд данные для создания парсеров."""
    logger.info('Получение данных по парсерам для создания в системе мониторинга')
    query = (
        "SELECT p.id as name, CONCAT(p.name, ', url: ', p.source) as description, sg.period_cron, sg.alert_timedelta "
        "FROM parser_source p JOIN source_group sg ON p.source_group_id = sg.id"
    )
    df_parsers = pd.read_sql(query, con=database.engine)
    df_parsers = pd.concat([df_parsers, get_saving_data_for_create()], ignore_index=True)
    logger.info('Данные получены по last_update_datetime')
    return df_parsers.replace({pd.NaT: None})


def get_parser_data_for_update() -> pd.DataFrame:
    """Вынимает из бд дату последнего обновления данных."""
    logger.info('Получение данных по парсерам для обновления времени парсинга в системе мониторинга')
    query = 'SELECT id as name, last_update_datetime FROM parser_source'
    df_parsers = pd.read_sql(query, con=database.engine)
    df_parsers = pd.concat([df_parsers, get_saving_data_for_update()], ignore_index=True)
    logger.info('Данные получены по last_update_datetime')
    return df_parsers.replace({pd.NaT: None})


def get_saving_data_for_create() -> pd.DataFrame:
    """Вынимает информацию по прасерам, у которых отслеживается время сохранения для создания парсеров."""
    logger.info('Получение данных по парсерам для создания в системе мониторинга')
    query = (
        "select concat(p.id, ' - сохранение') as name, CONCAT(p.name, ', url: ', p.source) as description, "
        "sg.period_cron, sg.alert_timedelta FROM parser_source p "
        "JOIN source_group sg ON p.source_group_id = sg.id "
        "where last_save_datetime is not Null"
    )
    df_parsers = pd.read_sql(query, con=database.engine)
    logger.info('Данные получены по last_save_datetime')
    return df_parsers


def get_saving_data_for_update() -> pd.DataFrame:
    """Вынимает информацию по прасерам, у которых отслеживается время сохранения."""
    logger.info('Получение информации по времени сохранения данных от парсеров')
    query = (
        "select concat(id, ' - сохранение') as name, last_save_datetime as last_update_datetime "
        "from parser_source where last_save_datetime is not Null"
    )
    df_parsers = pd.read_sql(query, con=database.engine)
    logger.info('Данные получены по last_save_datetime')
    return df_parsers
