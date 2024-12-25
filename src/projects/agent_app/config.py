"""Конфиг"""

import sys
from pathlib import Path

from environs import Env

sys.path.append(str(Path(__file__).absolute().parent.parent))

env = Env()
env.read_env()

psql_engine: str = env.str('PSQL_ENGINE', default='')

giga_credentials: str = env.str('GIGA_CREDENTIALS', default='')
giga_scope = 'GIGACHAT_API_CORP'
giga_model = 'GigaChat-Pro'
giga_agent_model = 'GigaChat-Max'

POST_TO_SERVICE_TIMEOUT = 60

WEB_RETRIEVER_PORT = env.int('WEB_RETRIEVER_PORT', default=447)

BASE_QA_BANKER_URL = 'http://213.171.8.248:8000'
BASE_QA_RESEARCH_URL = 'http://193.124.47.175:8000'
BASE_QA_WEB_URL = f'http://web_retriever_container:{WEB_RETRIEVER_PORT}'

MAX_FAILURE_TOLERANCE = 1

LOG_LEVEL = 20
LOG_FILE = 'agent_preparing_meeting'


#AGENT_MODEL = 'giga'
#AGENT_MODEL_TYPE = 'GigaChat-Max'
AGENT_MODEL = 'gpt'
AGENT_MODEL_TYPE = 'gpt-4o-mini'

MAX_TOKENS = 8000
TEMP = 0.00001

API_KEY = env.str('OPENAI_API_KEY', default='')
BASE_URL = 'https://api.vsegpt.ru/v1'

EXECUTION_CONFIG = {
    "recursion_limit": 100,
}

MESSAGE_AGENT_START = '📝Начало формирования отчета\n\n'
MESSAGE_RUN_CALL_REPORTS = '- Обработка Call Report`ов'
MESSAGE_RUN_CIB_REPORTS = '- Получение сводки из аналитического отчета CIB'
MESSAGE_RUN_RAG_NEWS = '- Формирования ответа из базы знаний по новостям'
MESSAGE_RUN_RAG_CIB = '- Формирования ответа из базы знаний по CIB'
MESSAGE_RUN_RAG_WEB = '- Получения данных из WEB'
MESSAGE_RUN_PRODUCT_RECOMMENDATION = '- Формирования рекомендаций по продуктам'
MESSAGE_RUN_NEWS = '- Обработка новостей'
