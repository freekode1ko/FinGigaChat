from pathlib import Path

from environs import Env

env = Env()
env.read_env()

PROJECT_DIR = Path(__file__).parent

LOG_FILE = 'bert_client_relevance'
LOG_LEVEL = 20  # INFO

DEBUG: bool = env.bool('DEBUG', default=False)

MODEL_PATH = 'hellcatAI/ruRoberta_client_relevance_classification'
