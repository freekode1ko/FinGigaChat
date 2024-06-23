"""Клас для получения файла из конфига редиса"""
import asyncio

from configs.config import BaseConfig
from db.redis.client import redis_client


class ConfigManager:
    """Класс для хранения конфига в редисе"""
    def __init__(self):
        self.__configs = [BaseConfig(), ]

        self.__loop = asyncio.get_event_loop()
        self.__loop.create_task(self.init_values())

    async def init_values(self):
        """Загрузка переменных в redis"""
        for config_class in self.__configs:
            for i in config_class.dict().items():
                await redis_client.set(f'settings_{i[0]}', i[1])

    def __getattr__(self, item):
        """Получение атрибута из редиса"""
        if (value := asyncio.run(redis_client.get(f'settings_{item}'))) is not None:
            return value
        for i in self.__configs:
            if item in i.dict():
                return getattr(i, item)

        raise AttributeError(f"Attribute '{item}' not found in Redis and configs")