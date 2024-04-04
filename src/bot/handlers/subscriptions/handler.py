from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware

from constants import subscriptions as callback_prefixes
from keyboards.subscriptions import constructors as kb_maker
from log.bot_logger import user_logger
from utils.base import user_in_whitelist, send_or_edit

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(F.data.startswith(callback_prefixes.END_WRITE_SUBS))
async def subs_menu_end(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню подписок

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(text='Формирование подписок завершено')


@router.callback_query(F.data.startswith(callback_prefixes.NEWS_SUBS_MENU))
async def news_subs_menu(callback_query: types.CallbackQuery) -> None:
    """
    Формирует сообщение с меню подписок на новости

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    keyboard = kb_maker.get_news_subscriptions_menu_kb()
    msg_text = 'Меню управления подписками на новости\n'
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)


async def subs_menu(message: types.CallbackQuery | types.Message) -> None:
    """Формирует меню подписок"""
    keyboard = kb_maker.get_subscriptions_menu_kb()
    msg_text = 'Меню управления подписками\n'
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(F.data.startswith(callback_prefixes.SUBS_MENU))
async def subscriptions_menu_callback(callback_query: types.CallbackQuery) -> None:
    """
    Получение меню для взаимодействия с подписками

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.CLIENT_SUBS_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await subs_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callback_prefixes.SUBS_MENU))
async def subscriptions_menu(message: types.Message) -> None:
    """
    Получение меню для взаимодействия с подписками

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await subs_menu(message)
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
