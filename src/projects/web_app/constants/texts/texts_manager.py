from dataclasses import dataclass

from db.redis import redis_client


@dataclass
class Text:
    key: str
    value: str
    name: str


class TextsManager:
    """
    Класс для получения констант из Redis.

    Должен быть инициализирован при старте приложения с помощью вызова
    асинхронного метода init().
    """
    PATTERN = 'settings_'

    # (!) Временное объявление разрешенных для редактирования ключей
    # Позже все будет в TextsManager из бота
    ALLOWED_KEYS = {
        'HELP_TEXT': 'Текст при старте бота',
        'REGISTRATION_NOT_WHITELIST_EMAIL': 'Пользователя нет в белом списке'
    }

    def _get_redis_key(self, key: str) -> str:
        """Возвращает ключ для Redis"""
        return f'{self.PATTERN}{key}'

    async def get_all(self) -> list[Text]:
        """Получение публичных констант из Redis"""
        redis_values = await redis_client.mget([self._get_redis_key(key) for key in self.ALLOWED_KEYS.keys() ])
        return [
            Text(key, redis_values[pos], value)
            for pos, (key, value) in enumerate(self.ALLOWED_KEYS.items())
        ]

    async def get(self, key: str) -> str:
        """Получение константы из Redis"""
        value = await redis_client.get(self._get_redis_key(key))
        if value is not None:
            return str(value)
        raise AttributeError(f'Значение для "{key}" не найдено в Redis')

    async def set(self, key: str, value: str) -> None:
        """Установка константы в Redis"""
        if key not in self.ALLOWED_KEYS:
            raise AttributeError(f'Невозможно установить значение для "{key}"')
        await redis_client.set(self._get_redis_key(key), value)


texts_manager = TextsManager()
