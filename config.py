import calendar
import json
import pathlib
from typing import Dict, List, Union
from datetime import timedelta

from environs import Env

from enums import Environment

env = Env()
env.read_env()

_env_value = env.str('ENV', default='local')
ENV: Environment = Environment.from_str(_env_value)

# config.py должен лежать в корне для правильного вычисления путей ко всем ассетам
PROJECT_DIR = pathlib.Path(__file__).parent  # noqa
STATIC_ASSETS_PATH = PROJECT_DIR / 'constants' / 'assets'


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

log_file = 'logs/{}.log'
LOG_LEVEL_DEBUG = 10
LOG_LEVEL_INFO = 20
LOG_LEVEL_WARNING = 30
LOG_LEVEL_ERROR = 40
LOG_LEVEL_CRITICAL = 50
log_lvl = LOG_LEVEL_DEBUG  # 10 -> DEBUG, 20 -> INFO, 30 -> WARNING, 40 -> ERROR, 50 -> CRITICAL

user_agents: List[str] = read_asset_from_json(file_name='user_agents.json')

list_of_companies: List[List] = read_asset_from_json('companies_list.json')

chat_base_url = 'https://beta.saluteai.sberdevices.ru/v1/'
research_base_url = 'https://research.sberbank-cib.com/'
data_market_base_url = 'https://markets.tradingeconomics.com/'
path_to_source = './sources'
user_cred = ('oddryabkov', 'gEq8oILFVFTV')  # ('nvzamuldinov', 'E-zZ5mRckID2')
api_key_gpt = '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'
research_cred = ('annekrasov@sberbank.ru', 'GfhjkmGfhjkm1')

RESEARCH_GETTING_TIMES_LIST = [
    '08:00', '10:00', '12:00', '14:00', '16:00',
    '17:00', '17:10', '17:20', '17:30', '17:40', '17:50', '18:00',
]

QUOTES_PROCESSING_PROC_NUM = 2

CLIENT_NAME_PATH = 'data/name/client_name.csv'
COMMODITY_NAME_PATH = 'data/name/commodity_name.csv'
CLIENT_ALTERNATIVE_NAME_PATH = 'data/name/client_with_alternative_names.xlsx'
COMMODITY_ALTERNATIVE_NAME_PATH = 'data/name/commodity_with_alternative_names.xlsx'
CLIENT_ALTERNATIVE_NAME_PATH_FOR_UPDATE = 'data/name/client_alternative.csv'
TELEGRAM_CHANNELS_DATA_PATH = pathlib.Path('sources') / 'tables' / 'tg_channels.xlsx'
QUOTES_SOURCES_PATH = pathlib.Path('sources') / 'ТЗ.xlsx'

BASE_GIGAPARSER_URL = 'http://gigaparsernews.ru:5000/{}'
NEWS_LIMIT = 5
USER_SUBSCRIPTIONS_LIMIT = 70
PAGE_ELEMENTS_COUNT = 10

# пассивная рассылка новостей по подпискам на тг каналы
# пн - 09:00 (за период с 16:00 прошлой пятницы дня до 09:00), 17:30 (за период с 09:00 этого дня до 17:30)
# вт, ср, чт - 09:00 (за период с 17:30 предыдущего дня до 09:00), 17:30 (за период с 09:00 этого дня до 17:30)
# пт - 09:00 (за период с 17:30 предыдущего дня до 09:00), 16:00 (за период с 16:00 предыдущей пятницы до 16:00)
TG_NEWSLETTER_EVERYDAY_PERIODS = [
    {
        'weekday': calendar.MONDAY,
        'send_time': '09:00',
        'timedelta': timedelta(hours=65),
    },
    {
        'weekday': calendar.MONDAY,
        'send_time': '17:30',
        'timedelta': timedelta(hours=8, minutes=30),
    },
    {
        'weekday': calendar.TUESDAY,
        'send_time': '09:00',
        'timedelta': timedelta(hours=15, minutes=30),
    },
    {
        'weekday': calendar.TUESDAY,
        'send_time': '17:30',
        'timedelta': timedelta(hours=8, minutes=30),
    },
    {
        'weekday': calendar.WEDNESDAY,
        'send_time': '09:00',
        'timedelta': timedelta(hours=15, minutes=30),
    },
    {
        'weekday': calendar.WEDNESDAY,
        'send_time': '17:30',
        'timedelta': timedelta(hours=8, minutes=30),
    },
    {
        'weekday': calendar.THURSDAY,
        'send_time': '09:00',
        'timedelta': timedelta(hours=15, minutes=30),
    },
    {
        'weekday': calendar.THURSDAY,
        'send_time': '17:30',
        'timedelta': timedelta(hours=8, minutes=30),
    },
    {
        'weekday': calendar.FRIDAY,
        'send_time': '09:00',
        'timedelta': timedelta(hours=15, minutes=30),
    },
    {
        'weekday': calendar.FRIDAY,
        'send_time': '16:00',
        'timedelta': timedelta(days=7),
    },
]

STATISTICS_PATH = 'statistics'
BOT_USAGE_STAT_FILE_NAME = 'bot_usage_statistics.xlsx'
USERS_DATA_FILE_NAME = 'users_catalog.xlsx'
NUM_DAYS_FOR_WHICH_STATS_COLLECT = 7
STATS_COLLECTOR_SLEEP_TIME = 60
POST_TO_GIGAPARSER_TIMEOUT = 180
POST_TO_GIGAPARSER_ATTEMPTS = 3
POST_TO_GIGAPARSER_SLEEP_AFTER_ERROR = 10

BASE_DATE_FORMAT = '%d.%m.%Y'
BASE_DATETIME_FORMAT = '%d.%m.%Y %H:%M'

INVERT_DATETIME_FORMAT = '%H:%M %d.%m.%Y'

mail_username = 'ai-helper@mail.ru'
mail_password = 'ExamKejCpmcpr8kM5emw'
mail_imap_server = 'imap.mail.ru'
summarization_prompt = (
    'Ты - суммаризатор новостной ленты.'
    'На вход тебе будут подаваться новости.'
    'Твоя задача - суммаризировать новость.'
    ''
    'Формат ответа:'
    '- суммаризация не должна быть слишком длинной;'
    '- тезисы должны быть лаконичными;'
    '- основная мысль не должна искажаться;'
    '- любые факты, которых не было в оригинальной статье, недопустимы;'
    '- нельзя использовать вводные слова, только текст суммаризации.'
    ''
    'ВАЖНО! Игнорировать формат ответа нельзя! Все условия должны соответствовать формату ответа!'
    ''
    '________________'
    'Твой ответ:'
)

help_text = (
    'Всем привет! Рады приветствовать Вас в AI-помощнике банкира!\n\n'
    'Для того, чтобы начать пользоваться ботом нужно ввести специальную команду для идентификации. '
    'Вы ее можете уточнить у Максима Королькова. \n\nБот позволяет оперативно получить информацию о ситуации на рынке, '
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
    'обратную связь по контенту, функционалу и новым идеям Максиму Королькову @korolkov_m и Александру Юдину.'
)

table_link = 'https://metals-wire.com/data'

charts_links = {
    'metals_wire_link': 'https://metals-wire.com/api/v2/charts/symbol/history/name_name/' '?to=date_date&countBack=1825',
    'investing_link': 'https://api.investing.com/api/financialdata/name_name/historical/chart/?period=P5Y&interval=P1M&pointscount=120',
}

dict_of_commodities: dict = read_asset_from_json('commodities_dict.json')
dict_of_companies: dict = read_asset_from_json('companies_dict.json')
industry_reviews: Dict[str, str] = read_asset_from_json('industry_reviews.json')

dict_of_emoji: dict = read_asset_from_json('emoji_dict.json')

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
SELENIUM_COMMAND_EXECUTOR = 'http://localhost:4444/wd/hub'
