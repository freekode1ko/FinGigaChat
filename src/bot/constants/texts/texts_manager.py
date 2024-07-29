"""Клас для получения файла из конфига редиса"""
from constants.texts.features import CONFIG_CLASSES
from db.redis.client import redis_client_sync as redis_client


class TextsManager:
    """Класс для хранения конфига в редисе"""

    def __init__(self):
        self.__configs = [x() for x in CONFIG_CLASSES]
        self.__init_values()

    def __init_values(self):
        """Загрузка переменных в redis"""
        for config_class in self.__configs:
            for key, value in config_class.dict().items():
                redis_client.set(f'settings_{key}', value)

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
