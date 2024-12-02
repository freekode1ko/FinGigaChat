"""Точка входа для отправки информации о времени сбора данных с источников в таблице parser_source."""
import time
import warnings

import schedule

from configs import config
from constants.enums import RequestType
from db import parser_source
from log.logger_base import logger
from module.auth import get_access_token
from module.formatter import ParserFormatter
from module.sender import SendToMonitoring


def send_to_monitoring(token: str, request_type: RequestType = RequestType.PUT) -> None:
    """Сборка полной статистики по использованию бота"""
    sending_obj = SendToMonitoring(token)
    match request_type:
        case RequestType.POST:
            getter_data_func = parser_source.get_parser_data_for_create
            sending_func = sending_obj.create_parsers
        case RequestType.PUT:
            getter_data_func = parser_source.get_parser_data_for_update
            sending_func = sending_obj.update_parsers_last_parsing_datetime
        case _:
            raise ValueError('Неизвестный тип запроса')

    data = getter_data_func()
    formatted_data = ParserFormatter.format(data, request_type)
    try:
        sending_func(formatted_data, timeout=config.POST_TO_SERVICE_TIMEOUT)
    except Exception as e:
        logger.exception(e)
        raise e


def main():
    """Сборщик статистики использования бота и справочника пользователей"""
    warnings.filterwarnings('ignore')

    logger.info('Аутентификация в системе мониторинга')
    token = get_access_token()
    logger.info('Инициализация сервиса отправки данных по статусам парсеров')
    send_to_monitoring(token, RequestType.POST)

    if config.DEBUG:
        while True:
            send_to_monitoring(token)
            time.sleep(60)

    # отправка данных по парсерам каждые config.SEND_STATUSES_EVERY_MINUTES минут
    schedule.every(config.SEND_STATUSES_EVERY_MINUTES).minutes.do(send_to_monitoring, token=token)

    while True:
        schedule.run_pending()
        time.sleep(config.PENDING_SLEEP_TIME)


if __name__ == '__main__':
    main()
