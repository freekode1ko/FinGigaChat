import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import callback_data_factories
from constants import constants


def get_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Аналитика sell-side ]
    [ Отраслевая аналитика ]
    [ MacroView ]
    [ Завершить ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Выбрать клиента из списка подписок',
        callback_data=callback_data_factories.SubscribedClients().pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text='Выбрать другого клиента',
        callback_data=callback_data_factories.UnsubscribedClients().pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.EndMenu().pack(),
    ))
    return keyboard.as_markup()


def get_clients_kb(item_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """

    """
    keyboard = InlineKeyboardBuilder()

    for _, item in item_df.iterrows():
        keyboard.row(types.InlineKeyboardButton(
            text=item['name'],
            callback_data=callback_data_factories.ClientMenu(client_id=item['id']).pack(),
        ))

    keyboard.row(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=callback_data_factories.Menu().pack(),
    ))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=callback_data_factories.EndMenu().pack(),
    ))
    return keyboard.as_markup()
