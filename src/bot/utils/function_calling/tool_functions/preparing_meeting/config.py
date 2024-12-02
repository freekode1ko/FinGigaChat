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
