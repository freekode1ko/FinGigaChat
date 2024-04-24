import os

import pandas as pd
from aiogram import types
from constants.products import product_shelf
from handlers.products.handler import router
from keyboards.products.product_shelf import callbacks, constructors as keyboards
from log.bot_logger import user_logger
from utils.base import send_pdf


@router.callback_query(callbacks.Menu.filter())
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.Menu) -> None:
    """
    Получение меню продуктовой полки

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    item_df = pd.DataFrame(product_shelf.PRODUCT_SHELF_DATA)
    item_df['id'] = item_df.index
    keyboard = keyboards.get_menu_kb(item_df)
    msg_text = product_shelf.TITLE
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetGroupFiles.filter())
async def get_group_files(callback_query: types.CallbackQuery, callback_data: callbacks.GetGroupFiles) -> None:
    """
    Получение пдф файлов для группы продуктовой полки

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    group_id = callback_data.group_id

    dir_path = product_shelf.PRODUCT_SHELF_DATA[group_id]['pdf_path']
    product_shelf_item = product_shelf.PRODUCT_SHELF_DATA[group_id]
    pdf_files = [dir_path / i for i in os.listdir(dir_path)] if dir_path else []

    msg_text = product_shelf_item['message_title']
    if not await send_pdf(callback_query, pdf_files, msg_text):
        msg_text = (
            f'{product_shelf.TITLE}\n'
            f'{product_shelf_item["name"]}\n'
            f'Функционал появится позднее'
        )
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
