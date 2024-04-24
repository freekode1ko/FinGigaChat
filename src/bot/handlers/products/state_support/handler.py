import os

from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

from constants import constants
from constants.products import state_support
from handlers.products.handler import router
from keyboards.products.state_support import callbacks
from log.bot_logger import user_logger


@router.callback_query(callbacks.GetStateSupportPDF.filter())
async def get_state_support_pdf(callback_query: types.CallbackQuery, callback_data: callbacks.GetStateSupportPDF) -> None:
    """
    Получение pdf файлов по господдержке

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    pdf_files = os.listdir(state_support.DATA_ROOT_PATH)
    if pdf_files:
        msg_text = state_support.TITLE
        await callback_query.message.answer(msg_text, parse_mode='HTML')

        for i in range(0, len(pdf_files), constants.TELEGRAM_MAX_MEDIA_ITEMS):
            media_group = MediaGroupBuilder()
            for fpath in pdf_files[i: i + constants.TELEGRAM_MAX_MEDIA_ITEMS]:
                media_group.add_document(media=types.FSInputFile(state_support.DATA_ROOT_PATH / fpath))

            await callback_query.message.answer_media_group(media_group.build())
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
