"""Конфиг для сервиса article"""
import json
import pathlib

from environs import Env

from constants.enums import Environment

env = Env()
env.read_env()

_env_value = env.str('ENV', default='local')
ENV: Environment = Environment.from_str(_env_value)

PROJECT_DIR = pathlib.Path(__file__).parent.parent  # noqa
STATIC_ASSETS_PATH = PROJECT_DIR / 'data' / 'assets'
DEBUG: bool = env.bool('DEBUG', default=False)

giga_credentials: str = env.str('GIGA_CREDENTIALS', default='')


def read_asset_from_json(file_name: str | pathlib.Path, encoding: str = 'utf-8') -> list | dict | str:
    """
    Считывает константу из json-файла

    :param file_name:   Путь до файла относительно STATIC_ASSETS_PATH
    :param encoding:    Кодировка файла
    :return:            Сериализованный JSON
    """
    return json.loads((STATIC_ASSETS_PATH / file_name).read_text(encoding=encoding))


SENTRY_POLYANALIST_PARSER_DSN: str = env.str('SENTRY_POLYANALIST_PARSER_DSN', default='')
SENTRY_FORCE_LOCAL: bool = env.bool('SENTRY_FORCE_LOCAL', default=False)

BASE_QABANKER_URL = 'http://213.171.8.248:8000/api/{}'

mail_imap_server = 'imap.mail.ru'
mail_username = 'ai-helper@mail.ru'
mail_password = 'ExamKejCpmcpr8kM5emw'

NEWS_LIMIT = 5
dict_of_emoji: dict = read_asset_from_json('emoji_dict.json')

psql_engine: str = env.str('PSQL_ENGINE', default='')

BASE_DATE_FORMAT = '%d.%m.%Y'

log_file = 'article'
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50
log_lvl = LOG_LEVEL_DEBUG  # 10 -> DEBUG, 20 -> INFO, 30 -> WARNING, 40 -> ERROR, 50 -> CRITICAL

api_key_gpt = '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'


giga_oauth_url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
giga_chat_url = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'
giga_scope = 'GIGACHAT_API_CORP'
giga_model = 'GigaChat-Pro'

ROBERTA_CLIENT_RELEVANCE_LINK = 'http://bert_client_relevance_container:444/query'
