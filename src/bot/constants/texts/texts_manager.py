"""Клас для получения файла из конфига редиса"""
import asyncio

from constants.texts.texts import AllListOfTexts, CallReportsTexts
from db.redis.client import redis_client_sync as redis_client


class TextsManager:
    """Класс для хранения конфига в редисе"""
    def __init__(self):
        self.__configs = [AllListOfTexts(), CallReportsTexts()]
        self.__init_values()

    def __init_values(self):
        """Загрузка переменных в redis"""
        for config_class in self.__configs:
            for i in config_class.dict().items():
                redis_client.set(f'settings_{i[0]}', i[1])

    def __getattr__(self, item):
        """Получение атрибута из редиса"""
        value = redis_client.get(f'settings_{item}')
        if value is not None:
            return value
        for config in self.__configs:
            if item in config.dict():
                return getattr(config, item)

        raise AttributeError(f"Attribute '{item}' not found in Redis and configs")


texts_manager = TextsManager()
