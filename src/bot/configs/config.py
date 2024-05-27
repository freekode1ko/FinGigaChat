import json
import pathlib
from typing import Union

from constants.enums import Environment
from environs import Env

env = Env()
env.read_env()

_env_value = env.str('ENV', default='local')
ENV: Environment = Environment.from_str(_env_value)

# config.py должен лежать в корне для правильного вычисления путей ко всем ассетам
PROJECT_DIR = pathlib.Path(__file__).parent.parent  # noqa
STATIC_ASSETS_PATH = PROJECT_DIR / 'data' / 'assets'
PATH_TO_SOURCES = PROJECT_DIR / 'sources'
TMP_VOICE_FILE_DIR = PROJECT_DIR / 'data' / 'voice'
TMP_VOICE_FILE_DIR.mkdir(parents=True, exist_ok=True)

DEBUG: bool = env.bool('DEBUG', default=False)


def read_asset_from_json(file_name: Union[str, pathlib.Path], encoding: str = 'utf-8') -> Union[list, dict, str]:
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

api_token: str = env.str('BOT_API_TOKEN', default='')
psql_engine: str = env.str('PSQL_ENGINE', default='')
redis_host: str = env.str('REDIS_HOST', default='0.0.0.0')
giga_credentials: str = env.str('GIGA_CREDENTIALS', default='')

DOMAIN_NAME: str = env.str('DOMAIN_NAME', default='localhost')

match DOMAIN_NAME:
    case 'ai-bankir-helper.ru':
        WEB_APP_URL = f'https://{DOMAIN_NAME}'
    case 'ai-bankir-helper-dev.ru':
        WEB_APP_URL = f'https://{DOMAIN_NAME}'
    case _:
        WEB_APP_URL = f'http://{DOMAIN_NAME}'


log_file = 'bot_runner'
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50
log_lvl = LOG_LEVEL_DEBUG  # 10 -> DEBUG, 20 -> INFO, 30 -> WARNING, 40 -> ERROR, 50 -> CRITICAL

giga_oauth_url = 'https://ngw.devices.sberbank.ru:9443'
giga_chat_url = 'https://gigachat.devices.sberbank.ru'
giga_scope = 'GIGACHAT_API_CORP'
giga_model = 'GigaChat-Pro'

# url к rag-сервисам
BASE_QA_BANKER_URL = 'http://213.171.8.248:8000'
BASE_STATE_SUPPORT_URL = 'http://89.223.65.160:8031'
POST_TO_SERVICE_TIMEOUT = 90

research_base_url = 'https://research.sberbank-cib.com/'
RESEARCH_SOURCE_URL = 'https://research.sberbank-cib.com/group/guest/publication?publicationId='
api_key_gpt = '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'

NEWS_LIMIT = 10
PAGE_ELEMENTS_COUNT = 10
CHECK_WEEKLY_PULSE_UPDATE_SLEEP_TIME = 60 * 5
USER_SUBSCRIPTIONS_LIMIT = 70
DELETE_TG_MESSAGES_TIMEOUT = 5

BASE_DATE_FORMAT = '%d.%m.%Y'
BASE_DATETIME_FORMAT = '%d.%m.%Y %H:%M'

INVERT_DATETIME_FORMAT = '%H:%M %d.%m.%Y'

MAIL_RU_LOGIN: str = env.str('MAIL_RU_LOGIN', default='')
MAIL_RU_PASSWORD: str = env.str('MAIL_RU_PASSWORD', default='')
mail_imap_server = 'imap.mail.ru'
mail_smpt_server = 'smtp.mail.ru'
mail_smpt_port = 465
mail_register_subject = 'Регистрация в AI-помощнике'


ECO_INAVIGATOR_URL = (
    'https://upd.mobile.sbrf.ru:10443/ios/dl/gdash/9845/1964'
    '#ewogICJ3aWRnZXRzIiA6IHsKICAgICIyODM2NDEiIDogewoKICAgIH0KICB9Cn0='
)

reg_mail_text = (
    'Добрый день!\n\nВы получили данное письмо, потому что указали данный адрес в AI-помощнике Банкира.\n\n'
    'Код для завершения регистрации:\n\n{}\n'
    'Никому не сообщайте этот код.'
)

new_user_start = (
    'Рады приветствовать Вас в AI-помощнике банкира!\n'
    'Для того, чтобы начать пользоваться ботом нужно пройти идентификацию.\n\n'
    'Введите корпоративную почту, на нее будет выслан код для завершения регистрации.'
)


help_text = (
    'Рады приветствовать Вас в AI-помощнике банкира!\n\n'
    'Бот позволяет оперативно получить информацию о ситуации на рынке, '
    'в отрасли, у клиента в сжатом виде.\n\nНа данный момент в AI-помощнике доступен следующий функционал и контент:\n'
    '—> новости по отраслям, клиентам, бенефициарам, ЛПР, commodities из более 200 источников '
    'включая ключевые отраслевые телеграмм каналы (есть возможность настроить ежедневную рассылку);\n'
    '—> аналитика CIB Research, включая финансовые показатели по публичным компаниям;\n'
    '—> актуальные рыночные котировки (экономика, FX, FI, commodities);\n'
    '—> общение с Gigachat.\n\n'
    'Получить данные в боте можно тремя способами:\n'
    '1) Зайти в боковое меню и кликнуть соответствующий раздел;\n'
    '2) Написать в строку поиска нужную команду (запрос);\n'
    '3) Настроить получение контента в режиме пуш-уведомлений (раздел меню «меню подписок»).\n\n'
    'Примеры полезных команд:\n'
    '🔘 Экономика\n🔘 Курс валют\n🔘 Газпром\n🔘 Дерипаска\n🔘 ОФЗ\n🔘 Инфляция\n🔘 Нефть\n'
    '🔘 Сырьевые товары\n🔘 ВВП\n🔘 Юань\n🔘 Золото\n🔘 Платежный баланс\n'
    '🔘 Напиши поздравление с днем рождения генеральному директору металлургической компании в деловом стиле\n'
    '🔘 Напиши поздравление с днем банковского работника\n🔘 Сделай саммари текста: «ТЕКСТ, КОТОРЫЙ НУЖНО СОКРАТИТЬ»\n'
    '\nТакже вы можете задавать любые вопросы, через команду общения с GigaChat "/gigachat", теоретического характера '
    'без привязки к актуальным данным, например: \n'
    'Что такое коэффициент конверсии комбикорма? Чем отличаются привилегированные акции от обыкновенных? '
    'Какие инструменты денежно-кредитной политики использует Банк России? И так далее.\n\n'
    'Для того, чтобы ежедневно получать новости по отраслям, клиентам, бенефициарам и commodities '
    'необходимо сформировать список интересующих вас подписок. Самый простой способ – подписаться на всю отрасль: \n'
    'в боковом меню нажать «Меню подписок» и следовать инструкции. \nНа данный момент доступны следующие отрасли: '
    'недвижимость, металлургия, телеком, торговля, энергетика, транспорт, промышленность, '
    'нетфегаз, сельское хозяйство, финансовые институты.\n\n'
    'Закрепите бота в своей ленте, чтобы не пропустить самый полезный контент и новости! '
    'Для этого сделайте долгое нажатие на бота в своей ленте новостей и в выпадающем списке нажмите «закрепить».\n\n'
    'Бот постоянно совершенствуется и дообучается, поэтому присылайте, пожалуйста, '
    'обратную связь по контенту, функционалу и новым идеям команде проекта.'
)

dict_of_emoji: dict = read_asset_from_json('emoji_dict.json')

WHISPER_MODEL = 'small'
