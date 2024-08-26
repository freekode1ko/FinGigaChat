from pathlib import Path

from environs import Env

env = Env()
env.read_env()

PROJECT_DIR = Path(__file__).parent

LOG_FILE = 'bert_commodity_relevance'
LOG_LEVEL = 20

DEBUG: bool = env.bool('DEBUG', default=False)

MODEL_PATH = 'hellcatAI/ruRoberta_commodity_relevance_classification_quant'
