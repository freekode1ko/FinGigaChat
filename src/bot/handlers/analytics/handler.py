"""Обработчики для меню Аналитика"""
import os
import tempfile
from pathlib import Path

from aiogram import F, Router, types
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from constants import analytics as callback_prefixes
from db.api.research import research_db
from db.whitelist import get_user
from keyboards.analytics import callbacks, constructors as keyboards
from log.bot_logger import user_logger
from module import formatter
from utils.base import bot_send_msg, send_or_edit, user_in_whitelist
from utils.watermark import add_watermark

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(F.data.startswith(callback_prefixes.END_MENU))
async def menu_end(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню аналитики

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(text='Просмотр аналитики завершен')


async def main_menu(message: types.CallbackQuery | types.Message) -> None:
    """
    Формирует меню аналитики

    :param message: types.CallbackQuery | types.Message
    """
    keyboard = keyboards.get_menu_kb()
    msg_text = (
        'В этом разделе вы можете получить, всесторонний анализ российского финансового рынка '
        'от SberCIB Investment Research'
    )
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(callbacks.AnalyticsMenu.filter())
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.AnalyticsMenu) -> None:
    """
    Получение меню для просмотра аналитики

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await main_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callbacks.AnalyticsMenu.__prefix__))
async def main_menu_command(message: types.Message) -> None:
    """
    Получение меню для просмотра аналитики

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await main_menu(message)
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(callbacks.GetFullResearch.filter())
async def get_full_version_of_research(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.GetFullResearch,
        session: AsyncSession,
) -> None:
    """
    Получить полную версию отчета

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   содержит дополнительную информацию по отчету
    :param session:         Асинхронная сессия базы данных.
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    research = await research_db.get(callback_data.research_id)
    formatted_msg_txt = formatter.ResearchFormatter.format(research)

    await bot_send_msg(callback_query.bot, chat_id, formatted_msg_txt)

    # Если есть файл - отправляем
    if research.filepath and os.path.exists(research.filepath):
        user = await get_user(session, from_user.id)
        user_anal_filepath = Path(tempfile.tempdir) / f'{os.path.basename(research["filepath"])}_{from_user.id}_watermarked.pdf'
        add_watermark(
            research.filepath,
            user_anal_filepath,
            user.user_email,
        )
        file = types.FSInputFile(user_anal_filepath)
        msg_txt = f'Полная версия отчета: <b>{research.header}</b>'
        await callback_query.message.answer_document(
            document=file,
            caption=msg_txt,
            parse_mode='HTML',
            protect_content=True,
        )

    try:
        await callback_query.message.delete()
    except TelegramAPIError:
        pass

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
