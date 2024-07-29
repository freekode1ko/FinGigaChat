"""Модуль с текстовыми константами по аналитическим отчетам CIB Research."""
from pydantic_settings import BaseSettings


class CibResearchTexts(BaseSettings):
    """Класс с текстовками по аналитическим отчетам CIB Research."""

    # Надпись "Источник: REPORT_SOURCE"
    REPORT_SOURCE: str = 'Sber CIB Investment Research'
