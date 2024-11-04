import config
from db.redis import redis_client
from log.logger_base import selector_logger
from .values import DEFAULT_VALUES


logger = selector_logger(config.LOG_FILE, config.LOG_LEVEL)


class TextsManagerError(Exception):
    """Исключение, возникающее при попытке обращения к неинициализированному менеджеру"""
    pass


class TextsManager:
    """
    Класс для получения констант из Redis.

    Должен быть инициализирован при старте приложения с помощью вызова
    асинхронного метода init().
    """
    PATTERN = 'settings_'

    def __init__(self):
        self.init_called = False

    async def init(self):
        """   
        Приоритет отдается константам, которые уже установлены в Redis.
        Это значит, что константы не будут изменены при инициализации этого
        класса. Однако будут добавлены те константы, которые используются
        в WebApp, но по какой-то причине отсутствуют в Redis.
        """
        for key, value in DEFAULT_VALUES.items():
            redis_value = await redis_client.get(f'{self.PATTERN}{key}')
            if not redis_value:
                await redis_client.set(f'{self.PATTERN}{key}', value)
            if redis_value and redis_value != str(value):
                logger.critical(
                    f'Значение "{value}" для ключа "{key}" не совпадает со значением "{redis_value}" в Redis'
                )
        self.init_called = True

    async def get(self, item):
        """Получение константы из Redis"""
        if not self.init_called:
            raise TextsManagerError('Необходимо инициализировать менеджер')
        value = await redis_client.get(f'{self.PATTERN}{item}')
        if value is not None:
            return value
        raise ValueError(f'Значение для "{item}" не найдено в Redis')


texts_manager = TextsManager()
