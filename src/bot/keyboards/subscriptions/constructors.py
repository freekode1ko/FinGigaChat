import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants.constants import DELETE_CROSS, PREV_PAGE, NEXT_PAGE, STOP, UNSELECTED, SELECTED
from constants.subscriptions import BACK_TO_MENU, TG_SUBS_DELETE_ALL_DONE, TG_SUBS_INDUSTRIES_MENU, \
    TG_SUBS_DELETE_ALL
from keyboards.subscriptions.callbacks import UserTGSubs, TGChannelMoreInfo, IndustryTGChannels, TGSubAction
from utils.bot.base import wrap_callback_data, unwrap_callback_data


def get_tg_subscriptions_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Просмотреть подписки ]
    [ Изменить подписки    ]
    [ Удалить все подписки ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Просмотреть подписки', callback_data=UserTGSubs(page=0).pack()))
    keyboard.row(types.InlineKeyboardButton(text='Изменить подписки', callback_data=TG_SUBS_INDUSTRIES_MENU))
    keyboard.row(types.InlineKeyboardButton(text='Удалить все подписки', callback_data=TG_SUBS_DELETE_ALL))
    return keyboard.as_markup()


def get_tg_subs_watch_kb(page_data: pd.DataFrame, page: int, max_pages: int) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ telegram channel name ][❌]
    [ telegram channel name ][❌]
    [ telegram channel name ][❌]
    [ <- ][     назад     ][ -> ]

    :param page_data: Данные о тг подписках на данной странице
    :param page: Номер страницы. Нужен для формирования callback_data
    :param max_pages: Всего страниц
    """
    keyboard = InlineKeyboardBuilder()

    for index, sub in page_data.iterrows():
        more_info_call = TGChannelMoreInfo(
            telegram_id=sub['id'],
            is_subscribed=True,
            back=wrap_callback_data(UserTGSubs(page=page).pack()),
        ).pack()
        delete_call = UserTGSubs(page=page, delete_tg_sub_id=sub['id']).pack()
        keyboard.row(types.InlineKeyboardButton(text=sub['name'], callback_data=more_info_call))
        keyboard.add(types.InlineKeyboardButton(text=DELETE_CROSS, callback_data=delete_call))

    if page != 0:
        keyboard.row(types.InlineKeyboardButton(text=PREV_PAGE, callback_data=UserTGSubs(page=page - 1).pack()))
    else:
        keyboard.row(types.InlineKeyboardButton(text=STOP, callback_data='stop'))

    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=BACK_TO_MENU))

    if page < max_pages - 1:
        keyboard.add(types.InlineKeyboardButton(text=NEXT_PAGE, callback_data=UserTGSubs(page=page + 1).pack()))
    else:
        keyboard.add(types.InlineKeyboardButton(text=STOP, callback_data='stop'))
    return keyboard.as_markup()


def get_tg_info_kb(telegram_id: int, is_subscribed: bool, back: str) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Подписаться/Удалить из подписок ]
    [   назад   ]

    :param is_subscribed: флаг, подписан ли пользователь на этот канал
    :param back: упакованные данные для callback_data
    """
    keyboard = InlineKeyboardBuilder()

    add_del_text = 'Подписаться' if not is_subscribed else 'Удалить из подписок'

    action_call = TGSubAction(
        telegram_id=telegram_id,
        need_add=not is_subscribed,
        back=back
    ).pack()
    keyboard.row(types.InlineKeyboardButton(text=add_del_text, callback_data=action_call))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=unwrap_callback_data(back)))
    return keyboard.as_markup()


def get_tg_subs_industries_menu_kb(industry_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Отрасль 1 ]
    ...
    [ Отрасль n ]
    [   назад   ]

    :param industry_df: DataFrame[id, name] инфа об отраслях
    """
    keyboard = InlineKeyboardBuilder()

    for index, industry in industry_df.iterrows():
        callback_meta = IndustryTGChannels(
            industry_id=industry['id'],
        )
        keyboard.row(types.InlineKeyboardButton(text=industry['name'].capitalize(), callback_data=callback_meta.pack()))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=BACK_TO_MENU))
    return keyboard.as_markup()


def get_industry_tg_channels_kb(industry_id: int, tg_channel_df: pd.DataFrame) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [][ канал 1 ]
    ...
    [][ канал n ]
    [   назад   ]

    :param industry_id: id отрасли
    :param tg_channel_df: DataFrame[id, name, is_signed] инфа о подборке подписок
    """
    keyboard = InlineKeyboardBuilder()

    for index, item in tg_channel_df.iterrows():
        add_del_call = IndustryTGChannels(
            industry_id=industry_id,
            telegram_id=item['id'],
            need_add=not item['is_subscribed']
        )
        more_info_call = TGChannelMoreInfo(
            telegram_id=item['id'],
            is_subscribed=item['is_subscribed'],
            back=wrap_callback_data(IndustryTGChannels(industry_id=industry_id).pack()),
        )
        mark = SELECTED if item['is_subscribed'] else UNSELECTED
        keyboard.row(types.InlineKeyboardButton(text=mark, callback_data=add_del_call.pack()))
        keyboard.add(types.InlineKeyboardButton(text=item['name'].capitalize(), callback_data=more_info_call.pack()))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=TG_SUBS_INDUSTRIES_MENU))
    return keyboard.as_markup()


def get_prepare_tg_subs_delete_all_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Да ][ Нет ]
    [   назад   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data=TG_SUBS_DELETE_ALL_DONE))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data=BACK_TO_MENU))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=BACK_TO_MENU))
    return keyboard.as_markup()


def get_back_to_tg_subs_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [   назад в меню   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=BACK_TO_MENU))
    return keyboard.as_markup()
