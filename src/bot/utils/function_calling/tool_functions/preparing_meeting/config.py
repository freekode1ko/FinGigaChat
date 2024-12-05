"""Конфиги"""

from environs import Env

env = Env()
env.read_env()

API_KEY = env.str('OPENAI_API_KEY', default='')
BASE_URL = 'https://api.vsegpt.ru/v1'
BASE_MODEL = 'openai/gpt-4o'

EXECUTION_CONFIG = {
    "recursion_limit": 50,
}

MESSAGE_AGENT_START = '📝Начало формирования отчета\n\n'
MESSAGE_RUN_CALL_REPORTS = '- Обработка Call Report`ов'
MESSAGE_RUN_CIB_REPORTS = '- Получение сводки из аналитического отчета CIB'
MESSAGE_RUN_RAG_NEWS = '- Обработка от рага по новостям'
MESSAGE_RUN_RAG_CIB = '- Обработка от рага по CIB'
MESSAGE_RUN_RAG_WEB = '- Обработка от рага WEB'
MESSAGE_RUN_PRODUCT_RECOMMENDATION = '- Формирования рекомендаций по продуктам'
MESSAGE_RUN_NEWS = '- Обработка новостей'
