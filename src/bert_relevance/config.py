from pathlib import Path

from environs import Env

env = Env()
env.read_env()

MODEL_TYPE = env.str('MODEL_TYPE')

PROJECT_DIR = Path(__file__).parent

LOG_FILE = f'bert_{MODEL_TYPE}_relevance'
LOG_LEVEL = 20  # INFO

DEBUG: bool = env.bool('DEBUG', default=False)

MODEL_PATH = f'hellcatAI/ruRoberta_{MODEL_TYPE}_relevance_classification_quant'
