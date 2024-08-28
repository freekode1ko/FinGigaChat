"""Конфиг для сервиса article_online."""
import pathlib

from constants.enums import Environment
from environs import Env

env = Env()
env.read_env()

_env_value = env.str('ENV', default='local')
ENV: Environment = Environment.from_str(_env_value)
STAND = 'prod' if ENV == Environment.PROD else 'test'

# config.py должен лежать в корне для правильного вычисления путей ко всем ассетам
PROJECT_DIR = pathlib.Path(__file__).parent.parent  # noqa
STATIC_ASSETS_PATH = PROJECT_DIR / 'data' / 'assets'
DEBUG: bool = env.bool('DEBUG', default=False)

SENTRY_NEWS_PARSER_DSN: str = env.str('SENTRY_NEWS_PARSER_DSN', default='')
SENTRY_FORCE_LOCAL: bool = env.bool('SENTRY_FORCE_LOCAL', default=False)
psql_engine: str = env.str('PSQL_ENGINE', default='')

log_file = 'article_online'
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50
log_lvl = LOG_LEVEL_DEBUG  # 10 -> DEBUG, 20 -> INFO, 30 -> WARNING, 40 -> ERROR, 50 -> CRITICAL

giga_credentials: str = env.str('GIGA_CREDENTIALS', default='')
giga_oauth_url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
giga_chat_url = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'
giga_scope = 'GIGACHAT_API_CORP'
giga_model = 'GigaChat-Pro'

BASE_GIGAPARSER_URL = 'http://gigaparsers.ru:7000/{}'
BASE_QABANKER_URL = 'http://213.171.8.248:8000/api/{}'
ROBERTA_CLIENT_RELEVANCE_LINK = 'http://bert_client_relevance_container:444/query'
ROBERTA_COMMODITY_RELEVANCE_LINK = 'http://bert_commodity_relevance_container:446/query'
# ROBERTA_COMMODITY_RELEVANCE_LINK = 'http://localhost:8000/query'

POST_TO_GIGAPARSER_TIMEOUT = 1200
POST_TO_SERVICE_TIMEOUT = 90
POST_TO_SERVICE_ATTEMPTS = 3
POST_TO_SERVICE_SLEEP_AFTER_ERROR = 10

BASE_DATETIME_FORMAT = '%d.%m.%Y %H:%M'
