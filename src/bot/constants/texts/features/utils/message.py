"""Модуль для хранения параметров отправки сообщений в тг боте"""
from pydantic_settings import BaseSettings


class TelegramMessageParams(BaseSettings):
    """Класс для хранения параметров отправки сообщений в тг боте"""

    PROTECT_CONTENT: str = 'True'
