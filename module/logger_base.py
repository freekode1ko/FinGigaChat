import datetime
import logging
import os
import re
import typing
from logging import Formatter, Handler, LogRecord
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Optional

from aiogram.types import Message
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
        self.handler = RotatingFileHandler(self.log_dir, maxBytes=MAX_BYTES, encoding='utf-8', delay=False, backupCount=1)

        logging.basicConfig(format=self.log_format, datefmt=self.log_datefmt, level=level, handlers=[self.handler])


LogLevelT = typing.TypeVar('LogLevelT', bound=int)
TelegramLoggerCallableT = Callable[[Message, str, Any], None]


class TelegramLogger:
    """
    Обертка над logging.Logger для логирования мета информации из тг-сообщения
    """

    def __init__(self, logger: Optional[logging.Logger] = None, *args, **kwargs):
        self.logger = logger or logging.Logger(__name__)

    @staticmethod
    def add_tg_message_meta(tg_msg: Message, msg: str) -> str:
        """
        Отформатировать текст, добавив мета-информацию из tg-сообщения
        Args:
            tg_msg: Объект aiogram.types.Message
            msg: текст
        Returns:
            Новый текст с метаинформацией из tg-сообщения
        """
        return f'*{tg_msg.chat.id} * {tg_msg.from_user.full_name} - {tg_msg.text}: {msg}'

    def log_tg_meta(self, tg_msg: Message, msg: str = '', level: LogLevelT = log_lvl, *args, **kwargs):
        """
        Логирует сообщения, добавляя мета-информацию о сообщении aiogram
        Args:
            tg_msg: Сообщение aiogram
            level: уровень логирования
            msg: сообщение, которое логируем
        """

        self.logger.log(msg=self.add_tg_message_meta(tg_msg, msg), level=level, *args, **kwargs)

    def get_callable_by_level(self, level: LogLevelT) -> TelegramLoggerCallableT:
        """
        Получить метод логера по уровню логирования
        Args:
            level: уровень логирования
        """
        _level_to_callable = {
            logging.INFO: self.info_tg_meta,
            logging.DEBUG: self.debug_tg_meta,
            logging.CRITICAL: self.critical_tg_meta,
            logging.WARNING: self.warning_tg_meta,
        }
        return _level_to_callable[level]

    def critical_tg_meta(self, tg_msg: Message, msg: str = '', *args, **kwargs):
        self.logger.critical(self.add_tg_message_meta(tg_msg, msg), *args, **kwargs)

    def info_tg_meta(self, tg_msg: Message, msg: str = '', *args, **kwargs):
        self.logger.info(self.add_tg_message_meta(tg_msg, msg), *args, **kwargs)

    def debug_tg_meta(self, tg_msg: Message, msg: str = '', *args, **kwargs):
        self.logger.debug(self.add_tg_message_meta(tg_msg, msg), *args, **kwargs)

    def warning_tg_meta(self, tg_msg: Message, msg: str = '', *args, **kwargs):
        self.logger.warning(self.add_tg_message_meta(tg_msg, msg), *args, **kwargs)


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
                f'insert into user_log (level, date, file_name, func_name, line_no, message, user_id) values '
                f"('{level}','{date}', '{file_name}','{func_name}',{line_no}, '{message}', {user_id})"
            )
            conn.execute(query)
            conn.commit()


def selector_logger(module_logger: str, level: int = log_lvl) -> Logger:
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


def get_handler(url_engine, level: int = log_lvl) -> DBHandler:
    return DBHandler(url_engine, level, LOG_FORMAT)


def get_db_logger(name, handler, level: int = log_lvl) -> logging.Logger:
    """Создает логер, который записывает в базу данных"""
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
