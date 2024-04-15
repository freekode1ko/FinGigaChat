from pathlib import Path

from environs import Env

PROJECT_DIR = Path(__file__).parent
STATIC_CERTS_PATH = PROJECT_DIR / 'data' / 'certs'
STATIC_CHAIN_PATH = STATIC_CERTS_PATH / 'fullchain.pem'
STATIC_KEY_PATH = STATIC_CERTS_PATH / 'privkey.pem'

env = Env()
env.read_env()

PSQL_ENGINE: str = env.str('PSQL_ENGINE', default='')

MEETING_PAGES = 'https://alinlpkv.github.io'

BASE_DATETIME_FORMAT = '%d.%m.%Y %H:%M'


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
        'msg': 'Встреча "{meeting_theme}" назначена на завтра'
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

