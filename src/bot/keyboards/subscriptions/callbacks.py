"""CallbackData по подпискам на каналы в телеграмме"""
from enum import auto, IntEnum
from typing import Optional

from aiogram.filters.callback_data import CallbackData


MENU = 'subscriptions_menu'


class SubsMenusEnum(IntEnum):
    """Уровни меню подписок на тг каналы"""

    main_menu = auto()

    # переход из main_menu
    my_subscriptions = auto()
    change_subscriptions = auto()
    delete_subscriptions = auto()
    delete_all_subscriptions = auto()


class SubsMenuData(CallbackData, prefix=MENU):
    """Меню подписок на тг каналы"""

    menu: SubsMenusEnum = SubsMenusEnum.main_menu
