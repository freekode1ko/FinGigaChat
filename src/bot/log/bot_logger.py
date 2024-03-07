from configs import config
from module.logger_base import get_db_logger, get_handler, selector_logger

# инициализируем обработчик и логгер
print('Инициализация логера')
handler = get_handler(config.psql_engine)
# логгер для сохранения пользовательских действий
user_logger = get_db_logger('bot_runner', handler)
# логгер для сохранения действий программы + пользователей
logger = selector_logger(config.log_file, config.LOG_LEVEL_INFO)
