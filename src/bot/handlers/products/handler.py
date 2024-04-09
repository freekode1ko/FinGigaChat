from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware

from constants import products as callback_prefixes
from keyboards.products import callbacks, constructors as keyboards
from log.bot_logger import user_logger
from utils.base import send_or_edit, user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(F.data.startswith(callback_prefixes.END_MENU))
async def menu_end(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню продукты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(text='Завершена работа с меню "продукты"')


async def main_menu(message: types.CallbackQuery | types.Message) -> None:
    """Формирует меню продукты"""
    keyboard = keyboards.get_menu_kb()
    msg_text = 'Продукты\n'
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(callbacks.ProductsMenu.filter())
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.ProductsMenu) -> None:
    """
    Получение меню продукты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await main_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callbacks.ProductsMenu.__prefix__))
async def main_menu_command(message: types.Message) -> None:
    """
    Получение меню продукты

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await main_menu(message)
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
