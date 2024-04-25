import os
from typing import Optional

import pandas as pd
from aiogram import types
from constants.products import hot_offers
from handlers.products.handler import router
from keyboards.products.hot_offers import callbacks
from keyboards.products.hot_offers import constructors as keyboards
from log.bot_logger import user_logger
from utils.base import send_pdf


@router.callback_query(callbacks.Menu.filter())
async def main_menu_callback(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.Menu,
        back_callback_data: Optional[str] = None,
) -> None:
    """
    Получение меню продуктовой полки

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    :param back_callback_data: callback_data для кнопки назад
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    item_df = pd.DataFrame(hot_offers.TABLE_DATA)
    item_df['id'] = item_df.index
    keyboard = keyboards.get_menu_kb(item_df, back_callback_data)
    msg_text = hot_offers.TITLE
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetHotOffersPDF.filter())
async def get_hot_offers_pdf(callback_query: types.CallbackQuery, callback_data: callbacks.CallbackData) -> None:
    """
    Получение pdf файлов по hot offers

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    group_id = callback_data.group_id

    dir_path = hot_offers.TABLE_DATA[group_id]['pdf_path']
    item = hot_offers.TABLE_DATA[group_id]
    pdf_files = [dir_path / f for f in os.listdir(dir_path)] if dir_path else []
    msg_text = item['message_title']
    
    if not await send_pdf(callback_query, pdf_files, msg_text):
        msg_text = (
            f'{hot_offers.TITLE}\n'
            f'{item["name"]}\n'
            f'Функционал появится позднее'
        )
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
