import pandas as pd
from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants.bot import constants
from constants.bot import subscriptions as callback_prefixes
from keyboards.subscriptions import callbacks
from utils.bot.base import unwrap_callback_data, wrap_callback_data


def get_approve_action_kb(yes_callback: str, no_callback: str, back_callback: str) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Да ][ Нет ]
    [   назад   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data=yes_callback))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data=no_callback))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=back_callback))
    return keyboard.as_markup()


def get_tg_subscriptions_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Просмотреть подписки ]
    [ Изменить подписки    ]
    [ Удалить все подписки ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(
            text='Просмотреть подписки',
            callback_data=callbacks.UserTGSubs(page=0).pack(),
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Изменить подписки',
            callback_data=callback_prefixes.TG_SUBS_INDUSTRIES_MENU,
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Удалить все подписки',
            callback_data=callback_prefixes.TG_SUBS_DELETE_ALL,
        )
    )
    keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data=callback_prefixes.TG_END_WRITE_SUBS))
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
        more_info_call = callbacks.TGChannelMoreInfo(
            telegram_id=sub['id'],
            is_subscribed=True,
            back=wrap_callback_data(callbacks.UserTGSubs(page=page).pack()),
        ).pack()
        delete_call = callbacks.UserTGSubs(page=page, delete_tg_sub_id=sub['id']).pack()
        keyboard.row(types.InlineKeyboardButton(text=sub['name'], callback_data=more_info_call))
        keyboard.add(types.InlineKeyboardButton(text=constants.DELETE_CROSS, callback_data=delete_call))

    if page != 0:
        keyboard.row(
            types.InlineKeyboardButton(
                text=constants.PREV_PAGE,
                callback_data=callbacks.UserTGSubs(page=page - 1).pack(),
            )
        )
    else:
        keyboard.row(types.InlineKeyboardButton(text=constants.STOP, callback_data='constants.STOP'))

    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.BACK_TO_TG_MENU))

    if page < max_pages - 1:
        keyboard.add(
            types.InlineKeyboardButton(
                text=constants.NEXT_PAGE,
                callback_data=callbacks.UserTGSubs(page=page + 1).pack(),
            )
        )
    else:
        keyboard.add(types.InlineKeyboardButton(text=constants.STOP, callback_data='constants.STOP'))
    keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data=callback_prefixes.TG_END_WRITE_SUBS))
    return keyboard.as_markup()


def get_tg_info_kb(telegram_id: int, is_subscribed: bool, back: str) -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Подписаться/Удалить из подписок ]
    [   назад   ]

    :param telegram_id: telegram_channel id
    :param is_subscribed: флаг, подписан ли пользователь на этот канал
    :param back: упакованные данные для callback_data
    """
    keyboard = InlineKeyboardBuilder()

    add_del_text = 'Подписаться' if not is_subscribed else 'Удалить из подписок'

    action_call = callbacks.TGSubAction(telegram_id=telegram_id, need_add=not is_subscribed, back=back).pack()
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
        callback_meta = callbacks.IndustryTGChannels(
            industry_id=industry['id'],
        )
        keyboard.row(types.InlineKeyboardButton(text=industry['name'].capitalize(), callback_data=callback_meta.pack()))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.BACK_TO_TG_MENU))
    keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data=callback_prefixes.TG_END_WRITE_SUBS))
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
        add_del_call = callbacks.IndustryTGChannels(
            industry_id=industry_id, telegram_id=item['id'], need_add=not item['is_subscribed']
        )
        more_info_call = callbacks.TGChannelMoreInfo(
            telegram_id=item['id'],
            is_subscribed=item['is_subscribed'],
            back=wrap_callback_data(callbacks.IndustryTGChannels(industry_id=industry_id).pack()),
        )
        mark = constants.SELECTED if item['is_subscribed'] else constants.UNSELECTED
        keyboard.row(types.InlineKeyboardButton(text=mark, callback_data=add_del_call.pack()))
        keyboard.add(types.InlineKeyboardButton(text=item['name'].capitalize(), callback_data=more_info_call.pack()))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.TG_SUBS_INDUSTRIES_MENU))
    keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data=callback_prefixes.TG_END_WRITE_SUBS))
    return keyboard.as_markup()


def get_prepare_tg_subs_delete_all_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Да ][ Нет ]
    [   назад   ]
    """
    return get_approve_action_kb(
        callback_prefixes.TG_SUBS_DELETE_ALL_DONE,
        callback_prefixes.BACK_TO_TG_MENU,
        callback_prefixes.BACK_TO_TG_MENU,
    )


def get_back_to_tg_subs_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [   назад в меню   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.BACK_TO_TG_MENU))
    return keyboard.as_markup()


def get_prepare_subs_delete_all_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Да ][ Нет ]
    [   назад   ]
    """
    return get_approve_action_kb(
        callback_prefixes.SUBS_DELETE_ALL_DONE,
        callback_prefixes.SUBS_MENU,
        callback_prefixes.SUBS_MENU,
    )


def get_back_to_subs_menu_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [   назад в меню   ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.SUBS_MENU))
    return keyboard.as_markup()


def get_subscriptions_kb() -> InlineKeyboardMarkup:
    """
    Формирует Inline клавиатуру вида:
    [ Список активных подписок ]
    [ Добавить новые подписки  ]
    [ Удалить подписки  ]
    [ Удалить все подписки ]
    """
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Список активных подписок', callback_data='myactivesubscriptions'))
    keyboard.row(types.InlineKeyboardButton(text='Добавить новые подписки', callback_data='addnewsubscriptions'))
    keyboard.row(types.InlineKeyboardButton(text='Удалить подписки', callback_data='deletesubscriptions'))
    keyboard.row(types.InlineKeyboardButton(text='Удалить все подписки', callback_data='deleteallsubscriptions'))
    keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data='end_write_subs'))
    return keyboard.as_markup()
