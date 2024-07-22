"""Клас для хранения текстовок"""
from pydantic_settings import BaseSettings


class AllListOfTexts(BaseSettings):
    """Класс для хранения текстовок, которы будут загружены в редис"""

    pass


class CallReportsTexts(BaseSettings):
    """Класс для хранения текстовок кол репортов"""

    CALL_REPORTS_MAIN_MENU: str = 'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?'
    CALL_REPORTS_CLOSE: str = 'Меню протоколов встреч закрыто.'


class WatermarkConfig(BaseSettings):
    """Класс для хранения параметров создания watermark"""

    FONT_TYPE: str = 'Helvetica'                            # Шрифт
    FONT_SIZE: int = 20                                     # Размер шрифта
    ROTATION: int = 45                                      # Угол наклона текста
    FONT_COLOR_ALPHA: float = 0.3                           # коэф прозрачности
    VERTICAL_REPETITIONS: int = 3                           # Кол-во строк на странице с вотермаркой
    HORIZONTAL_REPETITIONS: int = 3                         # Кол-во повторений слова в строке


CONFIG_CLASSES = [
    AllListOfTexts,
    CallReportsTexts,
    WatermarkConfig,
]
