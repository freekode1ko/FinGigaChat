import time
import warnings

import schedule

from configs import config
from db import parser_source
from log.logger_base import Logger, selector_logger
from module.formatter import ParserStatusFormatter
from module.sender import SendToMonitoring


def send_parser_statuses(logger: Logger.logger) -> None:
    """
    Сборка полной статистики по использованию бота

    :param logger: логгер
    """
    msg = 'Получение данных по парсерам'
    logger.info(msg)
    print(msg)
    # Get parser_source data with source_group data
    data = parser_source.get_parser_data()
    msg = 'Данные получены'
    logger.info(msg)
    print(msg)

    msg = 'Форматирование данных'
    logger.info(msg)
    print(msg)
    # Format data to send
    formatted_data = ParserStatusFormatter.format(data)
    msg = 'Данные отформатированы'
    logger.info(msg)
    print(msg)

    # send data to monitoring
    for i in range(config.POST_TO_SERVICE_ATTEMPTS):
        try:
            msg = 'Отправка данных на сервис мониторинг'
            logger.info(msg)
            print(msg)
            response = SendToMonitoring.send(formatted_data, timeout=config.POST_TO_SERVICE_TIMEOUT)
            msg = 'Данные отправлены: ответ %s'
            logger.info(msg, response)
            print(msg % response)
            break
        except Exception as e:
            msg = 'Ошибка при отправке данных: %s'
            logger.error(msg, e)
            print(msg % e)
            time.sleep(10)


def main():
    """Сборщик статистики использования бота и справочника пользователей"""
    warnings.filterwarnings('ignore')
    # логгер для сохранения действий программы + пользователей
    logger = selector_logger(config.log_file, config.LOG_LEVEL_INFO)

    msg = 'Инициализация сервиса отправки данных по статусам парсеров'
    logger.info(msg)
    print(msg)

    if config.DEBUG:
        while True:
            send_parser_statuses(logger)
            time.sleep(5 * 50)

    # отправка данных по парсерам каждые config.SEND_STATUSES_EVERY_MINUTES минут
    schedule.every(config.SEND_STATUSES_EVERY_MINUTES).minutes.do(send_parser_statuses, logger=logger)

    while True:
        schedule.run_pending()
        time.sleep(config.PENDING_SLEEP_TIME)


if __name__ == '__main__':
    main()
