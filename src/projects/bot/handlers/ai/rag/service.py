"""Business logic for Gen AI"""
from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from log.bot_logger import logger, user_logger


async def ask_genaidy(
        user_msg: str,
        message: types.Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    """Обработка запроса пользователя к Gen AI"""
    chat_id, full_name = message.chat.id, message.from_user.full_name
    logger.info(f'Start GenAIdy request handling: {chat_id=}, {message.message_id=}, {user_msg=}')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def prepare_to_meeting(
        user_msg: str,
        message: types.Message,
        state: FSMContext,
        session: AsyncSession,
) -> None:
    """Обработка запроса пользователя к Gen AI"""
    chat_id, full_name = message.chat.id, message.from_user.full_name
    logger.info(f'Start GenAIdy request handling: {chat_id=}, {message.message_id=}, {user_msg=}')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
