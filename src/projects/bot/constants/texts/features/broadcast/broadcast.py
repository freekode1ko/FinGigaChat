"""Модуль для общих на всего бота текстовок."""
from pydantic_settings import BaseSettings


class BroadcastTexts(BaseSettings):
    """Класс для общих на всего бота текстовок"""

    BROADCAST_PRODUCT_DEFAULT_ANSWER: str = (
        'Появилось новое актуальное предложение продукта Банка, '
        'ознакомьтесь с ним и по необходимости предложите клиенту.'
    )
