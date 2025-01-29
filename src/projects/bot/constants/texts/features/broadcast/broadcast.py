"""Модуль для текстовок по рассылкам."""
from pydantic_settings import BaseSettings


class BroadcastTexts(BaseSettings):
    """Класс для текстовок по рассылкам"""

    BROADCAST_PRODUCT_DEFAULT_ANSWER: str = (
        'Добрый день!\n' 
        'Предлагаем обсудить с клиентами новые продуктовые предложения:\n'
    )
