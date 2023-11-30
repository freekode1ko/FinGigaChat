import logging
from config import log_file, log_lvl


class Logger:
    logger = logging.getLogger(__name__)

    def __init__(self, log_name: str, level: int):
        """
        :param log_name: В какой файл писать. Если запуск установлен из main.py -> log_name=='Main'
        :param level: Установить уровень логирования
        """
        self.log_format = '%(asctime)s,%(msecs)d %(levelname)-8s [%(module)s:%(lineno)d in %(funcName)s] %(message)s'
        self.log_datefmt = '%d-%m-%Y %H:%M:%S'
        self.log_file = log_file.format(log_name)

        logging.basicConfig(filename=self.log_file, filemode="a", format=self.log_format,
                            datefmt=self.log_datefmt, level=level, encoding='utf-8')


def logger(module_logger: str):
    """
    Селектор для логера

    :param module_logger: Имя файла с точкой входа для логирования
    return Класс логера
    """
    if module_logger == 'main':
        return Logger('Main', log_lvl).logger
    elif module_logger == 'main_article':
        return Logger('Main_Article', log_lvl).logger
    elif module_logger == 'main_article_online':
        return Logger('Main_Article_Online', log_lvl).logger
    elif module_logger == 'bot_runner':
        return Logger('Bot_Runner', log_lvl).logger
    elif module_logger == 'test':
        return Logger('TEST', 10).logger
    else:
        print('Не найден сценарий для логирования')
