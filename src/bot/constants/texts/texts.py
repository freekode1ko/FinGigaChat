"""Клас для хранения текстовок"""
from pydantic_settings import BaseSettings
from reportlab.lib.units import mm


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
    WORD_SPACING: int = 50                                  # Расстояние между словами в строке
    LINE_SPACING: int = FONT_SIZE * 4                       # Расстояние между строк
    LINES_COUNT: int = 30                                   # Кол-во строк на странице с вотермаркой
    PAGE_SIZE: tuple[float, float] = (400 * mm, 400 * mm)   # Размер генерируемой страницы
    WORD_IN_LINE_COUNT: int = 8                             # Кол-во повторений слова в строке
    FONT_COLOR_ALPHA: float = 0.3                           # коэф прозрачности


CONFIG_CLASSES = [
    AllListOfTexts,
    CallReportsTexts,
    WatermarkConfig,
]
