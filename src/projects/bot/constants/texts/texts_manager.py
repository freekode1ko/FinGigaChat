"""Класс для работы с константами в Redis"""
from dataclasses import dataclass

from pydantic.fields import FieldInfo

from constants.texts.features import CONFIG_CLASSES
from db.redis.client import redis_client_sync as redis_client
from log.bot_logger import logger


@dataclass
class Text:
    """Информация о параметре из Redis"""
    key: str
    value: str
    name: str


class TextsManager:
    """Класс для хранения конфига в Redis"""

    PATTERN = 'settings_'

    def __init__(self):
        self._config_registry: dict[str, FieldInfo] = {}
        self._initialize()

    def _get_redis_key(self, key: str) -> str:
        """Получает ключ константы для Redis"""
        return f'{self.PATTERN}{key}'

    def _initialize(self) -> None:
        """Инициализация реестра параметров.
        
        По ключу хранится FieldInfo, Pydantic объект, позволяющий получить доступ к
        значению и человекочитаемому названию параметра. При инициализации происходит
        сверка с параметрами в Redis: если параметра нет или значения расходятся,
        то в Redis устанавливается значение по умолчанию.
        """
        save_to_redis = {}
        for config_cls in CONFIG_CLASSES:
            for field_key, field_info in config_cls().model_fields.items():
                self._config_registry[field_key] = field_info
                save_to_redis[self._get_redis_key(field_key)] = str(field_info.default)
        redis_values = redis_client.mget(save_to_redis.keys())
        for pos, (current_key, current_value) in enumerate(save_to_redis.items()):
            if redis_values[pos] is not None and redis_values[pos] != current_value:
                logger.critical(
                    f'Значение "{current_value}" для "{current_key}" не совпадает со значением "{redis_values[pos]}" в Redis.'
                )
        redis_client.mset(save_to_redis)

    def get_all(self) -> list[Text]:
        """Получает все публичные константы в виде списка объектов Text"""
        return [
            Text(key=key, value=getattr(self, key), name=str(field_info.title))
            for key, field_info in self._config_registry.items()
            if field_info.description == 'public'
        ]

    def set(self, key: str, value: str) -> None:
        """Устанавливает значение публичной константы в Redis"""
        if key not in self._config_registry or self._config_registry[key].description != 'public':
            raise AttributeError(f'Невозможно установить значение для "{key}"')
        redis_client.set(self._get_redis_key(key), value)

    def __getattr__(self, key: str) -> str:
        """Получает значение константы как атрибута класса"""
        value = redis_client.get(self._get_redis_key(key))
        if value is not None:
            return str(value)
        field_info = self._config_registry.get(key)
        if field_info is not None:
            return str(field_info.default)
        raise AttributeError(f'Атрибут "{key}" не найден в Redis и конфигах')


texts_manager = TextsManager()
