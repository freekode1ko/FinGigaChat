"""Файл с хендлерами макро обзора"""
import calendar
import datetime

from aiogram import types

from configs import config
from constants.analytics import macro_view
from handlers.analytics.handler import router
from keyboards.analytics.macro_view import callbacks
from log.bot_logger import user_logger
from utils.base import previous_weekday_date, send_pdf


@router.callback_query(callbacks.Menu.filter())
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.Menu) -> None:
    """
    Получение меню MacroView

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    monday_date = previous_weekday_date(datetime.date.today(), calendar.MONDAY)
    msg_text = macro_view.MESSAGE_TEXT_FORMAT.format(monday_date.strftime(config.BASE_DATE_FORMAT))
    files = [f for f in macro_view.FILES_PATH.iterdir() if f.exists()] if macro_view.FILES_PATH.exists() else []
    if not await send_pdf(callback_query, files, msg_text, protect_content=True):
        msg_text += '\nФункционал появится позднее'
        await callback_query.message.answer(msg_text, protect_content=True, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
