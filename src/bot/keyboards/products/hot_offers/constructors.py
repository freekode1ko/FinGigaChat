from typing import Optional

import pandas as pd
from aiogram.types import InlineKeyboardMarkup

from keyboards.products import constructors
from keyboards.products.hot_offers import callbacks


def get_menu_kb(item_df: pd.DataFrame, back_callback_data: Optional[str] = None) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]

    :param item_df: DataFrame[id, name]
    :param back_callback_data: callback_data для кнопки назад
    """
    return constructors.get_sub_menu_kb(item_df, callbacks.GetHotOffersPDF, back_callback_data)
