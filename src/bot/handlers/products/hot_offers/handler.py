import math
import os

from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder

from constants import constants
from constants.products import hot_offers
from handlers.products.handler import router
from keyboards.products.hot_offers import callbacks
from log.bot_logger import user_logger


@router.callback_query(callbacks.GetHotOffersPDF.filter())
async def get_state_support_pdf(callback_query: types.CallbackQuery, callback_data: callbacks.GetHotOffersPDF) -> None:
    """
    Получение pdf файлов по hot offers

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    pdf_files = os.listdir(hot_offers.DATA_ROOT_PATH)
    if pdf_files:
        msg_text = 'Актуальные предложения для клиента'
        await callback_query.message.answer(msg_text, protect_content=True, parse_mode='HTML')

        for i in range(math.ceil(len(pdf_files) / constants.TELEGRAM_MAX_MEDIA_ITEMS)):
            media_group = MediaGroupBuilder()
            for fpath in pdf_files[
                         i * constants.TELEGRAM_MAX_MEDIA_ITEMS: (i + 1) * constants.TELEGRAM_MAX_MEDIA_ITEMS]:
                media_group.add_document(media=types.FSInputFile(hot_offers.DATA_ROOT_PATH / fpath))

            await callback_query.message.answer_media_group(media_group.build(), protect_content=True)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
