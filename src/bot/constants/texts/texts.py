"""Клас для хранения текстовок"""
from pydantic_settings import BaseSettings


class AllListOfTexts(BaseSettings):
    """
    Класс для хранения текстовок, которы будут загружены в редис

    Examples:
    top_news_count: str = Field(3, env='TOP_NEWS_COUNT', default="1")
    DB_HOST: str = "123"
    DB_PORT: int = 123
    """

    pass


class CallReportsTexts(BaseSettings):
    """Класс для хранения текстовок кол репортов"""

    CALL_REPORTS_MAIN_MENU: str = 'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?'
    CALL_REPORTS_CLOSE: str = 'Меню протоколов встреч закрыто.'
