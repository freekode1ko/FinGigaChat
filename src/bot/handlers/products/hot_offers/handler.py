import math
import os

import pandas as pd
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

from constants import constants
from constants.products import hot_offers
from handlers.products.handler import router
from keyboards.products.hot_offers import callbacks
from keyboards.products.hot_offers import constructors as keyboards
from log.bot_logger import user_logger


@router.callback_query(callbacks.Menu.filter())
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.Menu) -> None:
    """
    Получение меню продуктовой полки

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    item_df = pd.DataFrame(hot_offers.TABLE_DATA)
    item_df['id'] = item_df.index
    keyboard = keyboards.get_menu_kb(item_df)
    msg_text = hot_offers.TITLE
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetHotOffersPDF.filter())
async def get_state_support_pdf(callback_query: types.CallbackQuery, callback_data: callbacks.GetHotOffersPDF) -> None:
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

    if pdf_files:
        msg_text = item['message_title']
        await callback_query.message.answer(msg_text, parse_mode='HTML')

        for i in range(0, len(pdf_files), constants.TELEGRAM_MAX_MEDIA_ITEMS):
            media_group = MediaGroupBuilder()
            for fpath in pdf_files[i: i + constants.TELEGRAM_MAX_MEDIA_ITEMS]:
                media_group.add_document(media=types.FSInputFile(fpath))

            await callback_query.message.answer_media_group(media_group.build())
    else:
        msg_text = (
            f'{hot_offers.TITLE}\n'
            f'{item["name"]}\n'
            f'Функционал появится позднее'
        )
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
