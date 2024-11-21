"""Конфиг для сервиса research"""
import json
import pathlib

from environs import Env

from constants.enums import Environment

env = Env()
env.read_env()

_env_value = env.str('ENV', default='local')
ENV: Environment = Environment.from_str(_env_value)

# config.py должен лежать в корне для правильного вычисления путей ко всем ассетам
PROJECT_DIR = pathlib.Path(__file__).parent.parent  # noqa
STATIC_ASSETS_PATH = PROJECT_DIR / 'data' / 'assets'
PATH_TO_SOURCES = PROJECT_DIR / 'sources'
PATH_TO_REPORTS = PROJECT_DIR / 'sources' / 'reports'
DEBUG: bool = env.bool('DEBUG', default=False)

PATH_TO_REPORTS.mkdir(parents=True, exist_ok=True)


def read_asset_from_json(file_name: str | pathlib.Path, encoding: str = 'utf-8') -> list | dict | str:
    """
    Считывает константу из json-файла

    Args:
        file_name: Путь до файла относительно STATIC_ASSETS_PATH
        encoding: Кодировка файла
    """
    return json.loads((STATIC_ASSETS_PATH / file_name).read_text(encoding=encoding))


SENTRY_CHAT_BOT_DSN: str = env.str('SENTRY_CHAT_BOT_DSN', default='')
SENTRY_QUOTES_PARSER_DSN: str = env.str('SENTRY_QUOTES_PARSER_DSN', default='')
SENTRY_RESEARCH_PARSER_DSN: str = env.str('SENTRY_RESEARCH_PARSER_DSN', default='')
SENTRY_POLYANALIST_PARSER_DSN: str = env.str('SENTRY_POLYANALIST_PARSER_DSN', default='')
SENTRY_NEWS_PARSER_DSN: str = env.str('SENTRY_NEWS_PARSER_DSN', default='')
SENTRY_FORCE_LOCAL: bool = env.bool('SENTRY_FORCE_LOCAL', default=False)

DB_USER: str = env.str('DB_USER', default='postgres')
DB_PASS: str = env.str('DB_PASS', default='password')
DB_HOST: str = env.str('DB_HOST', default='127.0.0.1')
DB_PORT: str = env.str('DB_PORT', default='5432')
DB_NAME: str = env.str('DB_NAME', default='postgres')
psql_engine: str = env.str('PSQL_ENGINE', default='')

log_file = 'research'
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50
log_lvl = LOG_LEVEL_DEBUG  # 10 -> DEBUG, 20 -> INFO, 30 -> WARNING, 40 -> ERROR, 50 -> CRITICAL

user_agents: list[str] = read_asset_from_json(file_name='user_agents.json')

list_of_companies: list[list] = read_asset_from_json('companies_list.json')

giga_oauth_url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
giga_chat_url = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'
giga_scope = 'GIGACHAT_API_CORP'
giga_model = 'GigaChat-Pro'

research_base_url = 'https://research.sberbank-cib.com/'
RESEARCH_LOGIN: str = env.str('RESEARCH_LOGIN')
RESEARCH_PASSWORD: str = env.str('RESEARCH_PASSWORD')
CIB_JSESSIONID = '1111akluq5tW31lGeafcXgItwuXYr_HUSdctex4U.pvlsa-respo0001'
CIB_LOGIN = '616e6e656b7261736f76407362657262616e6b2e7275'
CIB_PASSWORD = '336e52672b5048666739497856336549336d6c5069513d3d'
CIB_ID = '6c4b30425771657531317076614c375744757a5078413d3d'

RESEARCH_GETTING_TIMES_LIST = [
    '08:00',
    '09:00',
    '10:00',
    '11:00',
    '12:00',
    '13:00',
    '14:00',
    '15:00',
    '16:00',
    '17:00',
    '17:10',
    '17:20',
    '17:30',
    '17:40',
    '17:50',
    '18:00',
    '19:00',
    '20:00',
]

STATS_COLLECTOR_SLEEP_TIME = 60
POST_TO_SERVICE_ATTEMPTS = 3

BASE_DATETIME_FORMAT = '%d.%m.%Y %H:%M'
INVERT_DATETIME_FORMAT = '%H:%M %d.%m.%Y'

industry_reviews: dict[str, str] = read_asset_from_json('industry_reviews.json')

industry_base_url = (
    'https://research.sberbank-cib.com/group/guest/'
    'equities?sector={}#cibViewReportContainer_cibequitypublicationsportlet_'
    'WAR_cibpublicationsportlet_INSTANCE_gnfy_'
)

# SELENIUM CONTAINER PARAMS
# -d -p 4444:4444 -p 7900:7900 --shm-size="2g" --name="selenium" selenium/standalone-firefox:latest
SELENIUM_IMAGE_NAME = 'selenium/standalone-firefox:latest'
SELENIUM_CONTAINER_NAME = 'selenium'
SELENIUM_SHM_SIZE = '2g'
SELENIUM_PORTS = {
    4444: 4444,
    7900: 7900,
}
SELENIUM_RUN_KWARGS = {
    'image': SELENIUM_IMAGE_NAME,
    'name': SELENIUM_CONTAINER_NAME,
    'shm_size': SELENIUM_SHM_SIZE,
    'ports': SELENIUM_PORTS,
    'detach': True,
}

# SELENIUM DRIVER PARAMS
SELENIUM_COMMAND_EXECUTOR = 'http://selenium_firefox:4444/wd/hub'

# CIB API CONSTANTS
ARTICLE_URL = 'https://research.sberbank-cib.com/group/guest/publication'
MONTH_NAMES_DICT = {
    'янв': 1,
    'фев': 2,
    'мар': 3,
    'апр': 4,
    'мая': 5,
    'июн': 6,
    'июл': 7,
    'авг': 8,
    'сен': 9,
    'окт': 10,
    'ноя': 11,
    'дек': 12,
}
REPEAT_TRIES = 5
CONTENT_LENGTH__HTML_WITH_ARTICLE = 10000
