import logging
import os

from logging.handlers import RotatingFileHandler
from logging import Formatter, Handler, LogRecord
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from config import log_lvl


LOG_FORMAT = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(lineno)d in %(funcName)s] %(message)s'
MAX_BYTES = 10 * 1024 * 1024


class Logger:
    logger = logging.getLogger(__name__)

    def __init__(self, log_name: str, level: int):
        """
        :param log_name: В какой файл писать. Если запуск установлен из main.py -> log_name=='Main'
        :param level: Установить уровень логирования
        """
        self.log_dir = 'logs/{}/{}.log'.format(log_name, log_name)
        self.log_format = LOG_FORMAT
        self.log_datefmt = '%d-%m-%Y %H:%M:%S'
        self.handler = RotatingFileHandler(self.log_dir,
                                           maxBytes=MAX_BYTES, encoding='utf-8', delay=False, backupCount=1)

        logging.basicConfig(format=self.log_format, datefmt=self.log_datefmt, level=level, handlers=[self.handler])


def selector_logger(module_logger: str, level: int) -> logging.Logger:
    """
    Селектор для логера

    :param module_logger: Имя файла с точкой входа для логирования
    :param level: уровень логирования
    return Класс логера
    """
    logs_path = os.path.join('logs', module_logger)
    if not os.path.exists(logs_path):
        os.makedirs(logs_path, exist_ok=True)

    if not os.path.isdir(logs_path):
        raise FileExistsError(f'Файл {logs_path} не является каталогом')
    return Logger(module_logger, level).logger

class DBHandler(Handler):
    """Обработчик для сохранения журнальных сообщений в базу данных"""

    def __init__(self, url_engine: str, level: int, log_format: str):
        super().__init__()
        self.engine = create_engine(url_engine, poolclass=NullPool)
        self.setLevel(level)
        self.setFormatter(Formatter(log_format))

    def emit(self, record: LogRecord, *args) -> None:
        """Записывает в таблицу user_log атрибуты лога"""
        level = record.levelname
        date = datetime.datetime.fromtimestamp(record.created).replace(microsecond=0)
        file_name = record.module
        func_name = record.funcName
        line_no = record.lineno
        message = record.msg
        search_result = re.search(r'\*(.*?)\*', message)  # поиск айди пользователя в сообщении
        if search_result:
            user_id = search_result.group(1)
            message = message.replace(f'*{user_id}*', '').replace("'", "''")
        else:
            user_id = 'NULL'

        with self.engine.connect() as conn:
            query = text(
                'insert into user_log (level, date, file_name, func_name, line_no, message, user_id) values '
                '(:level, :date, :file_name, :func_name, :line_no, :message, :user_id)'
            )
            querykwargs = {
                'level': level,
                'date': date,
                'file_name': file_name,
                'func_name': func_name,
                'line_no': line_no,
                'message': message,
                'user_id': user_id,
            }
            conn.execute(query.bindparams(**querykwargs))
            conn.commit()

def get_handler(url_engine, level: int = log_lvl) -> DBHandler:
    """Получить хендлер"""
    return DBHandler(url_engine, level, LOG_FORMAT)


def get_db_logger(name, handler, level: int = log_lvl) -> logging.Logger:
    """Создает логер, который записывает в базу данных"""
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
