import os

from aiogram import types
from constants.products import hot_offers
from handlers.products.handler import router
from keyboards.products.hot_offers import callbacks
from log.bot_logger import user_logger
from utils.base import send_pdf


@router.callback_query(callbacks.GetHotOffersPDF.filter())
async def get_hot_offers_pdf(callback_query: types.CallbackQuery, callback_data: callbacks.CallbackData) -> None:
    """
    Получение pdf файлов по hot offers

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    pdf_files = [hot_offers.DATA_ROOT_PATH / i for i in os.listdir(hot_offers.DATA_ROOT_PATH)]
    msg_text = 'Актуальные предложения для клиента'
    await send_pdf(callback_query, pdf_files, msg_text)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
