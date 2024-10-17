from pathlib import Path

from environs import Env

env = Env()
env.read_env()

PROJECT_DIR = Path(__file__).parent

PORT = env.int('WEB_RETRIEVER_PORT', default=447)

LOG_FILE = env.str('LOG_FILE', default='web_retriever')
LOG_LEVEL = 20  # INFO

DEBUG: bool = env.bool('DEBUG', default=False)

# GIGA_MODEL = 'GigaChat-Pro'
GIGA_MODEL = "GigaChat-Pro-preview"
GIGA_SCOPE = 'GIGACHAT_API_CORP'
GIGA_CREDENTIALS: str = env.str('GIGA_CREDENTIALS', default='')
GIGA_URL = 'https://gigachat-preview.devices.sberbank.ru/api/v1'  # TODO: поменять ссылку перед выкаткой

N_NARROW_ANSWER = 2  # количество документов, которые используем для генерации вопроса
N_NORMAL_ANSWER = 5  # пытаемся сделать 3 ответа с разной развернутостью и берем тот,
N_WIDE_ANSWER = 8  # где больше ответ получился
STEP = 3  # константа количества шагов между количества возвращаемых ссылок

N_LINKS_AFTER_TOPIC = 2  # макс количество ссылок, которые оставляем после каждого параграфа
N_LINKS_AFTER_ANSWER = 3  # макс количество ссылок, которые оставляем после каждого ответа

DEDUPLICATION_THRESHOLD = 0.5
