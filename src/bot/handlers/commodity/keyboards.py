from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants
from handlers.commodity import callbacks


def get_menu_kb(commodity_id: int) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [ Новости ]
    [ Котировки ]
    [ Завершить ]

    :param commodity_id: Айди комода
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(
            text='Новости',
            callback_data=callbacks.CommodityMenuData(
                menu=callbacks.CommodityMenusEnum.choice_period,
                commodity_id=commodity_id,
            ).pack()
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Котировки',
            callback_data=callbacks.CommodityMenuData(
                menu=callbacks.CommodityMenusEnum.quotes,
                commodity_id=commodity_id,
            ).pack()
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Завершить',
            callback_data=callbacks.CommodityMenuData(
                menu=callbacks.CommodityMenusEnum.close,
                commodity_id=commodity_id,
            ).pack()
        )
    )
    return keyboard.as_markup()


def get_period_kb(commodity_id: int) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:

    [  Период 1   ]
    [     ...     ]
    [  Период N   ]
    [    Назад    ]
    [  Завершить  ]

    :param commodity_id: Айди комода
    """
    keyboard = InlineKeyboardBuilder()

    for period in constants.EXTENDED_GET_NEWS_PERIODS:
        keyboard.row(types.InlineKeyboardButton(
            text=period['text'],
            callback_data=callbacks.CommodityMenuData(
                menu=callbacks.CommodityMenusEnum.news,
                commodity_id=commodity_id,
                days_count=period['days'],
            ).pack(),
        ))

    keyboard.row(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data=callbacks.CommodityMenuData(
                menu=callbacks.CommodityMenusEnum.commodity_menu,
                commodity_id=commodity_id,
            ).pack()
        )
    )

    keyboard.row(
        types.InlineKeyboardButton(
            text='Завершить',
            callback_data=callbacks.CommodityMenuData(
                menu=callbacks.CommodityMenusEnum.close,
                commodity_id=commodity_id,
            ).pack()
        )
    )
    return keyboard.as_markup()
