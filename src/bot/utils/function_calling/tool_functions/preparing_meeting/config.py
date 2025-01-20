"""Конфиги"""

from environs import Env

env = Env()
env.read_env()

DEBUG_GRAPH = True

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
