import re
import datetime

import logging
from sqlalchemy import create_engine, text

from config import log_file, log_lvl


LOG_FORMAT = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(lineno)d in %(funcName)s] %(message)s'


class Logger:
    logger = logging.getLogger(__name__)

    def __init__(self, log_name: str, level: int):
        """
        :param log_name: В какой файл писать. Если запуск установлен из main.py -> log_name=='Main'
        :param level: Установить уровень логирования
        """
        self.log_format = LOG_FORMAT
        self.log_datefmt = '%d-%m-%Y %H:%M:%S'
        self.log_file = log_file.format(log_name)

        logging.basicConfig(filename=self.log_file, filemode="a", format=self.log_format,
                            datefmt=self.log_datefmt, level=level, encoding='utf-8')


class DBHandler(logging.Handler):
    """ Обработчик для сохранения журнальных сообщений в базу данных """

    def __init__(self, url_engine: str, level: int, log_format: str):
        super().__init__()
        self.engine = create_engine(url_engine, pool_pre_ping=True)
        self.setLevel(level)
        self.setFormatter(logging.Formatter(log_format))

    def emit(self, record: logging.LogRecord, *args) -> None:
        """ Записывает в таблицу user_log атрибуты лога """
        level = record.levelname
        date = datetime.datetime.fromtimestamp(record.created).replace(microsecond=0)
        file_name = record.module
        func_name = record.funcName
        line_no = record.lineno
        message = record.msg
        search_result = re.search(r'\*(.*?)\*', message)  # поиск айди пользователя в сообщении
        if search_result:
            user_id = search_result.group(1)
            message = message.replace(f'*{user_id}*', '')
        else:
            user_id = 'NULL'

        with self.engine.connect() as conn:
            query = text(f"insert into user_log (level, date, file_name, func_name, line_no, message, user_id) values "
                         f"('{level}','{date}', '{file_name}','{func_name}',{line_no}, '{message}', {user_id})")
            conn.execute(query)
            conn.commit()


def selector_logger(module_logger: str, level: int = log_lvl):
    """
    Селектор для логера

    :param module_logger: Имя файла с точкой входа для логирования
    :param level: уровень логирования
    return Класс логера
    """
    if module_logger == 'main':
        return Logger('Main', level).logger
    elif module_logger == 'main_article':
        return Logger('Main_Article', level).logger
    elif module_logger == 'main_article_online':
        return Logger('Main_Article_Online', level).logger
    elif module_logger == 'bot_runner':
        return Logger('Bot_Runner', level).logger
    elif module_logger == 'test':
        return Logger('TEST', 10).logger
    else:
        print('Не найден сценарий для логирования')


def get_handler(url_engine, level: int = log_lvl):
    return DBHandler(url_engine, level, LOG_FORMAT)


def get_db_logger(name, handler, level: int = log_lvl):
    """ Создает логер, который записывает в базу данных """
    logger = logging.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
