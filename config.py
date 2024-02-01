import json
import pathlib
from typing import Dict, List, Union

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


CLIENT_NAME_PATH = 'data/name/client_name.csv'
COMMODITY_NAME_PATH = 'data/name/commodity_name.csv'
CLIENT_ALTERNATIVE_NAME_PATH = 'data/name/client_with_alternative_names.xlsx'
COMMODITY_ALTERNATIVE_NAME_PATH = 'data/name/commodity_with_alternative_names.xlsx'
CLIENT_ALTERNATIVE_NAME_PATH_FOR_UPDATE = 'data/name/client_alternative.csv'
BASE_GIGAPARSER_URL = 'http://gigaparsernews.ru:5000/{}'
NEWS_LIMIT = 5
USER_SUBSCRIPTIONS_LIMIT = 20

STATISTICS_PATH = 'statistics'
BOT_USAGE_STAT_FILE_NAME = 'bot_usage_statistics.xlsx'
USERS_DATA_FILE_NAME = 'users_catalog.xlsx'
NUM_DAYS_FOR_WHICH_STATS_COLLECT = 7
STATS_COLLECTOR_SLEEP_TIME = 60

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
    'Всем привет! Мы начинаем пилотирование MVP AI-помощника банкира на ограниченной выборке ГКМ, старших '
    'банкиров и руководителей.\n\n'
    'В боте можно посмотреть аналитику CIB Research, текущие и прогнозные котировки и данные по макроэкономике,'
    ' FI, FX, сырьевым товарам воспользовавшись командами из бокового меню или ввести ключевые слова '
    '(экономика, валюты, ОФЗ, металлы, нефть, инфляция, КС, ВВП, бюджет, юань и тд).\n\n'
    'Для просмотра новостного потока по клиентам необходимо ввести название клиента («Роснефть», «Магнит», '
    '«Уралхим» и тд) - в настоящее время доступен сервис по 250 именам. По публичным клиентам доступны '
    'также исторические и прогнозные финансовые показатели.  Аналогичный новостной функционал, а также '
    'динамика котировок доступны по ключевым commodities.\n\n'
    'Кроме того, в боте вы можете пообщаться с Гигачатом в свободной форме, попросив написать письмо, сделать '
    'самари, перевести текст и тд.\n\n'
    'В ближайших планах: расширение функционала в части отраслевой аналитики, персонализация под ГКМ и '
    'настройка пассивного контента (настройка рассылки), инфо по законодательству, госпраммам и многое другое!\n\n'
    'В перспективе рассматриваем варианты заведения колл репортов через этот бот и интеграцию с контуром '
    'альфа (тут есть ограничения по безопасности, но мы не сдаемся и ищем варианты:)\n\n'
    'Бот постоянно совершенствуется и дообучается, поэтому присылайте, пожалуйста, обратную связь по контенту, '
    'функционалу и новым идеям Максиму Королькову @korolkov_m и Александру Юдину.'
)

table_link = 'https://metals-wire.com/data'

charts_links = {
    'metals_wire_link': 'https://metals-wire.com/api/v2/charts/symbol/history/name_name/' '?to=date_date&countBack=1825',
    'investing_link': 'https://api.investing.com/api/financialdata/name_name/historical/chart/'
    '?period=P5Y&interval=P1M&pointscount=120',
}

dict_of_commodities: dict = read_asset_from_json('commodities_dict.json')
dict_of_companies: dict = read_asset_from_json('companies_dict.json')
industry_reviews: Dict[str, str] = read_asset_from_json('industry_reviews.json')

industry_base_url = (
    'https://research.sberbank-cib.com/group/guest/'
    'equities?sector={}#cibViewReportContainer_cibequitypublicationsportlet_'
    'WAR_cibpublicationsportlet_INSTANCE_gnfy_'
)
