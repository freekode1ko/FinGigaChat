import os

import pandas as pd
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

from constants.products import product_shelf
from handlers.products.handler import router
from keyboards.products.product_shelf import callbacks, constructors as keyboards
from log.bot_logger import user_logger


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
    msg_text = 'Продуктовая полка'
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.GetGroupPDF.filter())
async def get_group_pdf(callback_query: types.CallbackQuery, callback_data: callbacks.GetGroupPDF) -> None:
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
    product_shelf_item_name = product_shelf.PRODUCT_SHELF_DATA[group_id]["name"]
    pdf_files = os.listdir(dir_path) if dir_path else []

    if pdf_files:
        media_group = MediaGroupBuilder(caption=product_shelf_item_name)
        for fpath in pdf_files:
            media_group.add_document(media=types.FSInputFile(dir_path / fpath))

        await callback_query.message.answer_media_group(media_group.build(), protect_content=True)
    else:
        msg_text = (
            f'Продуктовая полка\n'
            f'{product_shelf_item_name}\n'
            f'На данный момент, информация в системе отсутствует'
        )
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
