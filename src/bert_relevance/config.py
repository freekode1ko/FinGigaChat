from pathlib import Path

from environs import Env

env = Env()
env.read_env()

PROJECT_DIR = Path(__file__).parent

LOG_FILE = env.str('LOG_FILE')
LOG_LEVEL = 20  # INFO

DEBUG: bool = env.bool('DEBUG', default=False)

MODEL_PATH = env.str('MODEL_PATH')
