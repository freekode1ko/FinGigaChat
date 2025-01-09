"""Конфиг для сервиса parser_monitoring"""
import json
import pathlib

from environs import Env
from pytz import timezone

from constants.enums import Environment

env = Env()
env.read_env()

_env_value = env.str('ENV', default='local')
ENV: Environment = Environment.from_str(_env_value)

# config.py должен лежать в корне для правильного вычисления путей ко всем ассетам
PROJECT_DIR = pathlib.Path(__file__).parent.parent  # noqa
STATIC_ASSETS_PATH = PROJECT_DIR / 'data' / 'assets'
DEBUG: bool = env.bool('DEBUG', default=False)

SOURCE_SYSTEM = f'AI_helper_{_env_value}'
MONITORING_USER_LOGIN: str = env.str('MONITORING_USER_LOGIN')
MONITORING_USER_PASSWORD: str = env.str('MONITORING_USER_PASSWORD')
MONITORING_URL_BASE: str = str(env.str('MONITORING_URL_BASE', default='')) + '/api/v1'
MONITORING_LOGIN_URL: str = MONITORING_URL_BASE + '/auth/login'
MONITORING_SYSTEM_URL = f'{MONITORING_URL_BASE}/source_systems/{SOURCE_SYSTEM}'
MONITORING_PARSER_URL = f'{MONITORING_SYSTEM_URL}/parsers'


def read_asset_from_json(file_name: str | pathlib.Path, encoding: str = 'utf-8') -> list | dict | str:
    """
    Считывает константу из json-файла

    Args:
        file_name: Путь до файла относительно STATIC_ASSETS_PATH
        encoding: Кодировка файла
    """
    return json.loads((STATIC_ASSETS_PATH / file_name).read_text(encoding=encoding))


psql_engine: str = env.str('PSQL_ENGINE', default='')

log_file = 'parser_monitoring'
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50
log_lvl = LOG_LEVEL_DEBUG  # 10 -> DEBUG, 20 -> INFO, 30 -> WARNING, 40 -> ERROR, 50 -> CRITICAL

SEND_STATUSES_EVERY_MINUTES = 5
PENDING_SLEEP_TIME = 60

POST_TO_SERVICE_TIMEOUT = 90
POST_TO_SERVICE_ATTEMPTS = 3

UTC_TZ = timezone('UTC')
MOSCOW_TZ = timezone('Europe/Moscow')
