import os

import pandas as pd
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

from constants import constants
from constants.analytics import industry
from handlers.analytics.handler import router
from keyboards.analytics.industry import callbacks, constructors as keyboards
from log.bot_logger import user_logger


@router.callback_query(callbacks.Menu.filter())
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.Menu) -> None:
    """
    Получение меню Отраслевая аналитика

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    pdf_files = os.listdir(industry.DATA_ROOT_PATH)
    if pdf_files:
        msg_text = 'Отраслевая аналитика'
        await callback_query.message.answer(msg_text, protect_content=True, parse_mode='HTML')

        for i in range(0, len(pdf_files), constants.TELEGRAM_MAX_MEDIA_ITEMS):
            media_group = MediaGroupBuilder()
            for fpath in pdf_files[i: i + constants.TELEGRAM_MAX_MEDIA_ITEMS]:
                media_group.add_document(media=types.FSInputFile(industry.DATA_ROOT_PATH / fpath))

            await callback_query.message.answer_media_group(media_group.build(), protect_content=True)
    else:
        item_df = pd.DataFrame()
        keyboard = keyboards.get_menu_kb(item_df)
        msg_text = (
            'Отраслевая аналитика\n\n'
            'Функционал появится позднее'
        )
        await callback_query.message.edit_text(msg_text, reply_markup=keyboard)

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
