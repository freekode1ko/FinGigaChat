"""CallbackData для макро обзора"""
from aiogram.filters.callback_data import CallbackData

from constants.analytics import macro_view as callback_prefixes


class Menu(CallbackData, prefix=callback_prefixes.MENU):
    """CallbackData для макро обзора"""

    pass


class GetGroupSections(CallbackData, prefix=callback_prefixes.SECTIONS):
    """Меню разделов для группы group_id"""

    group_id: int
