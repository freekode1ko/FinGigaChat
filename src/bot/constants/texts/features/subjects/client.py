"""Модуль с текстовыми константами по взаимодействию с клиентами."""
from pydantic_settings import BaseSettings


class ClientInfoTexts(BaseSettings):
    """Класс с текстовками по данным о клиентах."""

    CHOOSE_CLIENT_SECTION: str = 'Выберите раздел для получения данных по клиенту <b>{name}</b>'
