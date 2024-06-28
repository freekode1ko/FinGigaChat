"""Клас для хранения текстовок"""
from pydantic_settings import BaseSettings


class AllListOfTexts(BaseSettings):
    """
    Класс для хранения текстовок, которы будут загружены в редис
    """

    pass


class CallReportsTexts(BaseSettings):
    """Класс для хранения текстовок кол репортов"""

    CALL_REPORTS_MAIN_MENU: str = 'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?'
    CALL_REPORTS_CLOSE: str = 'Меню протоколов встреч закрыто.'


CONFIG_CLASSES = [AllListOfTexts, CallReportsTexts]
