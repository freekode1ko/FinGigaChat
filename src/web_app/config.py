from environs import Env

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

