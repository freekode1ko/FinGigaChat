"""Инициализации"""

from log.logger_base import selector_logger
from config import LOG_FILE, LOG_LEVEL

logger = selector_logger(LOG_FILE, LOG_LEVEL)
