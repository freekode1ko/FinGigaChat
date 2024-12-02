"""Модуль отправки данных на сервис мониторинг"""
import time

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from configs import config
from constants.enums import RequestType
from log.logger_base import logger
from module.auth import get_access_token
from schemas.parser import ParserCreate, ParserUpdateLastUpdateTime


class ParserCreationError(Exception):
    """Ошибка при создании парсинга"""


class ParserUpdatingError(Exception):
    """Ошибка при обновлении парсинга"""


class SendToMonitoring:
    """Класс отправки данных в мониторинг"""

    def __init__(self, token: str):
        self.headers = {
            'Authorization': f'Bearer {token}',
            'source-system': config.SOURCE_SYSTEM,
            'event-timestamp': str(int(time.time())),
            'Content-type': 'application/json',
            'accept': '*/*',
        }

    def _handle_authorization_error(self, method: RequestType, url: str, json_data: dict | list, **kwargs):
        """Обновление токена."""
        self.headers['Authorization'] = f'Bearer {get_access_token()}'
        return requests.request(method=method, url=url, headers=self.headers, json=json_data, **kwargs)

    @retry(
        stop=stop_after_attempt(config.POST_TO_SERVICE_ATTEMPTS),
        wait=wait_fixed(10),
        retry=retry_if_exception_type((requests.ConnectionError, requests.ReadTimeout))
    )
    def send_request(self, method: RequestType, url: str, json_data: dict | list, **kwargs):
        """Отправка запроса."""
        logger.info('Отправка запроса')
        r = requests.request(method=method, url=url, headers=self.headers, json=json_data, **kwargs)
        if r.status_code == 401:
            r = self._handle_authorization_error(method, url, json_data, **kwargs)
        return r

    def update_parser(self, parser_name: str, json_data: dict, **kwargs):
        """Парсер уже существует, отправка запроса на обновление"""
        r = self.send_request(
            method=RequestType.update, url=f'{config.MONITORING_PARSER_URL}/{parser_name}',
            json_data=json_data, **kwargs,
        )
        if r.status_code == 200:
            logger.info(f'Парсер "{parser_name}" обновлен')
        else:
            raise ParserUpdatingError(f'Возникла проблема при обновлении парсера "{parser_name}": {r.text}')

    def create_parsers(self, parsers_data: list[ParserCreate], **kwargs):
        """Создание парсеров, если их нет, если есть, то обновление данных."""
        logger.info('Отправка данных для создания/обновления данных о парсерах на сервис мониторинг: %s', parsers_data)
        for parser in parsers_data:
            json_data = parser.model_dump(mode='json', exclude_none=True)
            r = self.send_request(
                method=RequestType.create, url=config.MONITORING_PARSER_URL,
                json_data=json_data, **kwargs,
            )

            match r.status_code:
                case 201:
                    logger.info(f'Парсер "{parser.name}" создан')
                case 409:
                    logger.info(f'Парсер "{parser.name}" уже существует, отправка запроса на обновление')
                    self.update_parser(parser.name, json_data, **kwargs)
                case _:
                    raise ParserCreationError(f'Возникла проблема при создании парсера "{parser.name}": {r.text}')

    def update_parsers_last_parsing_datetime(self, data: list[ParserUpdateLastUpdateTime], **kwargs):
        """
        Отправить даты последнего парсинга в сервис мониторинга.

        :param data:    Данные о парсерах.
        :param kwargs:  Доп параметры для отправки put-запроса (все допустимые, кроме url, headers, json).
        """
        logger.info('Отправка данных по обновлению дат парсинга на сервис мониторинг: %s', data)
        r = self.send_request(
            method=RequestType.update, url=config.MONITORING_PARSER_URL,
            json_data=[parser.model_dump(mode='json') for parser in data], **kwargs,
        )
        if r.status_code == 200:
            logger.info(f'Парсеры обновлены: ответ %s', r)
        else:
            raise ParserUpdatingError(f'Возникла проблема при обновлении парсеров: {r.text}')
