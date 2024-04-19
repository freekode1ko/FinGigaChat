import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import constants


def get_pagination_kb(
        page_data: pd.DataFrame,
        current_page: int,
        max_pages: int,
        next_page_callback: str,
        prev_page_callback: str,
        back_callback: str,
        end_callback: str,
        reverse: bool = False,
) -> InlineKeyboardMarkup:
    """
    [action (action_callback)][ item_name 1 (item_callback) ]
    ...
    [action (action_callback)][ item_name N (item_callback) ]
    [<-][ Назад ][->]
    [ Завершить ]
    :param page_data: DataFrame[name, item_callback[, action, action_callback]]
    :param current_page: Номер страницы. Нужен для формирования callback_data
    :param max_pages: Всего страниц
    :param next_page_callback: callback_data для кнопки ->
    :param prev_page_callback: callback_data для кнопки <-
    :param back_callback: callback_data для кнопки назад
    :param end_callback: callback_data для кнопки Завершить
    :param reverse: Меняет местами кнопки action и item_name
    """
    keyboard = InlineKeyboardBuilder()

    for _, item in page_data.iterrows():
        buttons = []
        if item.get('action') and item.get('action_callback'):
            buttons.append(types.InlineKeyboardButton(text=item['action'], callback_data=item['action_callback']))
        buttons.append(types.InlineKeyboardButton(text=item['name'], callback_data=item['item_callback']))

        keyboard.row(*(buttons[::-1] if reverse else buttons))

    if current_page != 0:
        keyboard.row(types.InlineKeyboardButton(
            text=constants.PREV_PAGE,
            callback_data=prev_page_callback,
        ))
    else:
        keyboard.row(types.InlineKeyboardButton(text=constants.STOP, callback_data='constants.STOP'))

    keyboard.add(types.InlineKeyboardButton(
        text=constants.BACK_BUTTON_TXT,
        callback_data=back_callback,
    ))

    if current_page < max_pages - 1:
        keyboard.add(types.InlineKeyboardButton(
            text=constants.NEXT_PAGE,
            callback_data=next_page_callback,
        ))
    else:
        keyboard.add(types.InlineKeyboardButton(text=constants.STOP,
                                                callback_data='constants.STOP'))
    keyboard.row(types.InlineKeyboardButton(
        text=constants.END_BUTTON_TXT,
        callback_data=end_callback,
    ))
    return keyboard.as_markup()
