"""Модуль отправки данных на сервис мониторинг"""
import time
from uuid import uuid4

import requests

from configs import config
from schemas.parser import ParserStatusSend


class SendToMonitoring:
    """Класс отправки данных в мониторинг"""

    API_KEY: str = config.api_key
    SOURCE_SYSTEM: str = config.source_system

    @classmethod
    def send(cls, data: list[ParserStatusSend], **kwargs) -> requests.Response:
        """
        Отправить статусы парсеров в сервис мониторинга

        Args:
            data:       Статусы парсеров
            **kwargs:   Доп параметры для отправки post-запроса

        Returns:
            Возвращает результат отправки запроса
        """
        json_data = [i.model_dump(mode='json') for i in data]
        if config.monitoring_api_url != '/{}':
            r = requests.post(
                config.monitoring_api_url.format(config.update_parser_statuses_url),
                headers={
                    'access_token': config.api_key,
                    'source-system': config.source_system,
                    'request-uuid': str(uuid4()),
                    'event-timestamp': str(int(time.time())),
                    'Content-type': 'application/json',
                    'accept': '*/*',
                },
                json=json_data,
                **kwargs,
            )
            return r
