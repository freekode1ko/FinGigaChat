"""Константы для запуска приложения"""
import json
import pathlib
from typing import Union

from environs import Env

from constants.enums import Environment

env = Env()
env.read_env()

_env_value = env.str('ENV', default='local')
ENV: Environment = Environment.from_str(_env_value)

# config.py должен лежать в корне для правильного вычисления путей ко всем ассетам
PROJECT_DIR = pathlib.Path(__file__).parent.parent  # noqa
STATIC_ASSETS_PATH = PROJECT_DIR / 'data' / 'assets'
DEBUG: bool = env.bool('DEBUG', default=False)


def read_asset_from_json(file_name: Union[str, pathlib.Path], encoding: str = 'utf-8') -> Union[list, dict, str]:
    """
    Считывает константу из json файла

    :param file_name: Имя файла или путь к файлу, который необходимо прочитать.
    :param encoding: Кодировка файла. По умолчанию 'utf-8'.
    :return:  Содержимое JSON файла в виде списка, словаря или строки.
    """
    return json.loads((STATIC_ASSETS_PATH / file_name).read_text(encoding=encoding))


SENTRY_QUOTES_PARSER_DSN: str = env.str('SENTRY_QUOTES_PARSER_DSN', default='')
SENTRY_FORCE_LOCAL: bool = env.bool('SENTRY_FORCE_LOCAL', default=False)

psql_engine: str = env.str('PSQL_ENGINE', default='')

log_file = 'quotes'
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50
log_lvl = LOG_LEVEL_DEBUG  # 10 -> DEBUG, 20 -> INFO, 30 -> WARNING, 40 -> ERROR, 50 -> CRITICAL

user_agents: list[str] = read_asset_from_json(file_name='user_agents.json')

path_to_source = './sources'

QUOTES_PROCESSING_PROC_NUM = 2

PAGE_ELEMENTS_COUNT = 10

BASE_DATETIME_FORMAT = '%d.%m.%Y %H:%M'

INVERT_DATETIME_FORMAT = '%H:%M %d.%m.%Y'

tradingeconomics_commodities: dict = read_asset_from_json('tradingeconomics_commodities.json')

COLLECT_PERIOD = '15m'
