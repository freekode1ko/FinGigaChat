"""Модуль для хранения параметров WebApp в тг боте"""
from pydantic_settings import BaseSettings


class TelegramWebAppParams(BaseSettings):
    """Класс для хранения параметров WebApp сообщений в тг боте"""

    WEBAPP_SHOW_BUTTONS: str = 'False'
