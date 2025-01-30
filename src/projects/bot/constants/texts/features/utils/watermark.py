"""Модуль для хранения параметров создания watermark"""
from pydantic_settings import BaseSettings


class WatermarkConfig(BaseSettings):
    """Класс для хранения параметров создания watermark"""

    FONT_TYPE: str = 'Helvetica'                            # Шрифт
    FONT_SIZE: int = 20                                     # Размер шрифта
    ROTATION: int = 45                                      # Угол наклона текста
    FONT_COLOR_ALPHA: float = 0.1                           # коэф прозрачности
    VERTICAL_REPETITIONS: int = 2                           # Кол-во строк на странице с вотермаркой
    HORIZONTAL_REPETITIONS: int = 2                         # Кол-во повторений слова в строке
