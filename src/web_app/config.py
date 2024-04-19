import json
from pathlib import Path

from environs import Env

PROJECT_DIR = Path(__file__).parent
STATIC_CERTS_PATH = PROJECT_DIR / 'data' / 'certs'
STATIC_CHAIN_PATH = STATIC_CERTS_PATH / 'fullchain.pem'
STATIC_KEY_PATH = STATIC_CERTS_PATH / 'privkey.pem'
JS_CONFIG_PATH = PROJECT_DIR / 'frontend' / 'static' / 'config.json'
JS_CONFIG_PATH.touch(exist_ok=True)

LOG_FILE = 'web_app'
LOG_LEVEL = 20  # info


# ______________________________env____________________________
env = Env()
env.read_env()

DEBUG: bool = env.bool('DEBUG', default=False)
PSQL_ENGINE: str = env.str('PSQL_ENGINE', default='')
DOMAIN_NAME: str = env.str('DOMAIN_NAME', default='localhost')


# ___________________________config_js_________________________
match DOMAIN_NAME:
    case 'ai-bankir-helper.ru':
        WEB_APP_URL = f'https://{DOMAIN_NAME}'
    case 'ai-bankir-helper-dev.ru':
        WEB_APP_URL = f'https://{DOMAIN_NAME}'
    case _:
        WEB_APP_URL = f'http://{DOMAIN_NAME}'

with open(JS_CONFIG_PATH, 'w') as file:
    json.dump({"WEB_APP_URL": WEB_APP_URL}, file)


# _________________________date_format_________________________
SERVER_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
BASE_DATETIME_FORMAT = '%d.%m.%Y %H:%M'
BASE_TIME_FORMAT = '%H:%M'


# ____________________________email____________________________
MAIL_RU_LOGIN: str = env.str('MAIL_RU_LOGIN', default='')
MAIL_RU_PASSWORD: str = env.str('MAIL_RU_PASSWORD', default='')
MAIL_SMTP_SERVER = 'smtp.mail.ru'
MAIL_SMTP_PORT = 465


# ____________________________schedular____________________________
BOT_API_TOKEN: str = env.str('BOT_API_TOKEN', default='')
REMEMBER_TIME = {  # за сколько минут нужно напомнить о встрече и каким сообщением
    'first': {
        'minutes': 24 * 60,
        'msg': 'Встреча "{meeting_theme}" назначена на завтра в {time}'
    },
    'second': {
        'minutes': 60,
        'msg': 'Встреча "{meeting_theme}" начнется через час'
    },
    'last': {
        'minutes': 15,
        'msg': 'Встреча "{meeting_theme}" начнется через 15 минут'
    }
}
