from enum import IntEnum, auto
from typing import Optional

from aiogram.filters.callback_data import CallbackData


MENU = 'tg_subs'


class TelegramSubsMenusEnum(IntEnum):
    """Уровни меню подписок на тг каналы"""
    # Выбор тг группы
    main_menu = auto()
    # Завершение работы с меню
    end_menu = auto()

    # переход из main_menu
    group_main_menu = auto()

    # переход из group_main_menu
    my_subscriptions = auto()
    change_subscriptions = auto()
    delete_subscriptions = auto()

    # переход из my_subscriptions
    telegram_channel_info = auto()

    # переход из change_subscriptions
    telegram_channels_by_section = auto()

    # переход из delete_subscriptions
    approve_delete_menu = auto()

    # переход из approve_delete_menu
    delete_subscriptions_by_group = auto()


class TelegramSubsMenuData(CallbackData, prefix=MENU):
    """Меню подписок на тг каналы"""
    menu: TelegramSubsMenusEnum
    group_id: int = 0
    section_id: int = 0
    telegram_id: int = 0
    page: int = 0
    is_subscribed: bool = False
    need_add: Optional[bool] = None
    back_menu: TelegramSubsMenusEnum = TelegramSubsMenusEnum.main_menu
