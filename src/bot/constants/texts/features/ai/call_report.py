"""Модуль с текстовыми константами по call report."""
from pydantic_settings import BaseSettings


class CallReportsTexts(BaseSettings):
    """Класс для хранения текстовок кол репортов"""

    CALL_REPORTS_MAIN_MENU: str = 'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?'
    CALL_REPORTS_CLOSE: str = 'Меню протоколов встреч закрыто.'
