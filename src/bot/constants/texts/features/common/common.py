"""Модуль для общих на всего бота текстовок."""
from pydantic_settings import BaseSettings


class CommonTexts(BaseSettings):
    """Класс для общих на всего бота текстовок"""

    COMMON_FEATURE_WILL_APPEAR: str = '\nФункционал появится позднее'
