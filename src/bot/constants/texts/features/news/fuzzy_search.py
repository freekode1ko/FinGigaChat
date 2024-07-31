"""Модуль с текстовками для работы с неточным поиском."""
from pydantic_settings import BaseSettings


class FuzzySearchTexts(BaseSettings):
    """Класс с текстовками для работы с неточным поиском."""

    # Текстовки для отображения кнопок с найденными неточным поиском клиентами, коммодами, отраслями
    FORMAT_BUTTON_NEAREST_TO_SUBJECT: str = '{subject_name} {additional_info}'

    # Доп инфа для кнопок при неточном поиске
    CLIENT_ADDITIONAL_INFO: str = '(получить инфо о компании)'
    COMMODITY_ADDITIONAL_INFO: str = '(получить новости по сырью)'
    INDUSTRY_ADDITIONAL_INFO: str = '(получить новости по отрасли)'
    STAKEHOLDER_ADDITIONAL_INFO: str = '(получить новости из СМИ)'
