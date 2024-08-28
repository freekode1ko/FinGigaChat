"""Модуль для общих на всего бота текстовок."""
from pydantic_settings import BaseSettings


class CommonTexts(BaseSettings):
    """Класс для общих на всего бота текстовок"""

    COMMON_CANCEL_WORD: str = 'отмена'

    COMMON_CANCEL_MSG: str = f'Напишите «{COMMON_CANCEL_WORD}» для очистки'

    COMMON_FEATURE_WILL_APPEAR: str = '\nФункционал появится позднее'

    COMMON_DATE_OF_DATA: str = 'Данные на {date}'

    COMMON_CLARIFYING_REQUEST: str = (
        'Уточните, пожалуйста, ваш запрос..\n\n'
        'Возможно, вы имели в виду один из следующих вариантов:'
    )
