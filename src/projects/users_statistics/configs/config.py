"""Конфиг для сервиса users_statistics"""
import pathlib

from environs import Env

from constants.enums import Environment

env = Env()
env.read_env()

_env_value = env.str('ENV', default='local')
ENV: Environment = Environment.from_str(_env_value)

PROJECT_DIR = pathlib.Path(__file__).parent.parent  # noqa
DEBUG: bool = env.bool('DEBUG', default=True)

psql_engine: str = env.str('PSQL_ENGINE', default='')

log_file = 'users_statistics'
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50
log_lvl = LOG_LEVEL_DEBUG  # 10 -> DEBUG, 20 -> INFO, 30 -> WARNING, 40 -> ERROR, 50 -> CRITICAL

STATISTICS_PATH = pathlib.Path('statistics')
NUM_DAYS_FOR_WHICH_STATS_COLLECT = 7
STATS_COLLECTOR_SLEEP_TIME = 60

# STMP SETTINGS
MAIL_USER: str = env.str('MAIL_RU_LOGIN', default='')
MAIL_PASS: str = env.str('MAIL_RU_PASSWORD', default='')
MAIL_STMP_HOST = 'smtp.mail.ru'
MAIL_STMP_PORT = 465

STATISTICS_RECIPIENTS = env.list('STATISTICS_RECIPIENTS', delimiter=',', default=[])  # Почты взять у Никиты
STATISTICS_IGNORE_TG_IDS = env.list('STATISTICS_IGNORE_TG_IDS', delimiter=',', default=[])  # это tg_id разрабов
# Взаимодействие пользователя с гигой
STATISTICS_PROMPT_FUNCTIONS = env.list('STATISTICS_PROMPT_FUNCTIONS', delimiter=',', default=[
    'giga_ask',
    'ask_giga_chat',
    '_request_to_rag_api',
    '_request_to_giga',
    '_request_to_api',
])
STATISTICS_FROM_DATE = env.date('STATISTICS_FROM_DATE', default='2023-01-01')  # С какой даты собирается статистика
STATISTICS_SUBJECT = 'Статистика по ai-помощнику банкира'
