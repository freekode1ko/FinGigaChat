from enum import auto, IntEnum

from aiogram.filters.callback_data import CallbackData

from constants.analytics import industry as callback_prefixes
from constants.enums import IndustryTypes


class MenuEnum(IntEnum):
    # Меню с выбором отрасли
    main_menu = auto()

    # Выдача аналитики по отрасли
    get_industry_anal = auto()


class Menu(CallbackData, prefix=callback_prefixes.MENU):
    """Данные для колбэков в меню отраслейвой аналитики"""

    menu: MenuEnum = MenuEnum.main_menu
    industry_id: int | None = None
    industry_type: IndustryTypes = IndustryTypes.default
