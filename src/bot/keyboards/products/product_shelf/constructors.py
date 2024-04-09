import pandas as pd
from aiogram.types import InlineKeyboardMarkup

from keyboards.products import constructors
from keyboards.products.product_shelf import callbacks


def get_menu_kb(item_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Группа 1 ]
    ...
    [ Группа n ]
    [  назад  ]

    :param item_df: DataFrame[id, name]
    """
    return constructors.get_sub_menu_kb(item_df, callbacks.GetGroupPDF)
