"""Модуль для текстовок по рассылкам."""
from pydantic_settings import BaseSettings


class BroadcastTexts(BaseSettings):
    """Класс для текстовок по рассылкам"""

    BROADCAST_PRODUCT_DEFAULT_ANSWER: str = (
        'Появилось новое актуальное предложение по продуктам Банка, '
        'ознакомьтесь с ним и по необходимости предложите клиенту.'
    )
