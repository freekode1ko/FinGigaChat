"""Обработка общения пользователя с GigaChat."""
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from constants.constants import giga_ans_footer
from handlers.ai.handler import router
from log.bot_logger import logger, user_logger
import module.gigachat as gig
from utils.base import user_in_whitelist


chat = gig.GigaChat(logger)


class GigaChatState(StatesGroup):
    """Автомат состояний общения с GigaChat."""

    gigachat_mode = State()
    gigachat_query = State()


@router.message(Command('gigachat'))
async def set_gigachat_mode(message: types.Message, state: FSMContext) -> None:
    """
    Переключение в режим общения с Gigachat.

    :param message:     Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param state:       Объект, который хранит состояние FSM для пользователя.
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        await state.set_state(GigaChatState.gigachat_mode)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

        cancel_command = 'завершить'
        cancel_msg = f'Напишите «{cancel_command}» для завершения общения с Gigachat'
        msg_text = 'Начато общение с Gigachat\n\n' + cancel_msg

        buttons = [[types.KeyboardButton(text=cancel_command)]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True, input_field_placeholder=cancel_msg, one_time_keyboard=True
        )

        data = await state.get_data()
        first_user_query = data.get('gigachat_query', None)

        if first_user_query:
            await message.answer(f'Подождите...\nФормирую ответ на запрос: "{first_user_query}"\n{cancel_msg}',
                                 reply_markup=keyboard)
            await ask_giga_chat(message, first_user_query)
        else:
            await message.answer(msg_text, reply_markup=keyboard)

    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.message(GigaChatState.gigachat_mode)
async def handler_gigachat_mode(message: types.Message) -> None:
    """Отправка пользователю ответа, сформированного Gigachat, на сообщение пользователя."""
    await ask_giga_chat(message)


def _get_response(chat_id: int, full_name: str, query: str) -> str:
    """
    Получение и форматирование ответа от GigaChat.

    :param chat_id:     Telegram id пользователя.
    :param full_name:   Полное имя пользователя.
    :param query:       Запрос пользователя (перефразированный с помощью GigaChat)
    :return:            Отформатированный ответ на запрос.
    """
    try:
        giga_answer = chat.get_giga_answer(text=query)
        user_logger.info(f'*{chat_id}* {full_name} - "{query}" : На запрос GigaChat ответил: "{giga_answer}"')
        response = f'{giga_answer}\n\n{giga_ans_footer}'
    except Exception as e:
        logger.critical(f'ERROR : GigaChat не сформировал ответ по причине: {e}"')
        user_logger.critical(f'*{chat_id}* {full_name} - "{query}" : GigaChat не сформировал ответ по причине: {e}"')
        response = 'Извините, я пока не могу ответить на ваш запрос'

    return response


async def ask_giga_chat(message: types.Message, first_user_query: str = '') -> None:
    """
    Отправляет ответ на запрос пользователя.

    :param message:             Message от пользователя.
    :param first_user_query:    Запрос от пользователя вне режима GigaChat.
    """
    user_query = first_user_query if first_user_query else message.text
    chat_id, full_name = message.chat.id, message.from_user.full_name
    await message.bot.send_chat_action(message.chat.id, 'typing')

    response = _get_response(chat_id, full_name, user_query)
    await message.answer(response, parse_mode='HTML', disable_web_page_preview=True)
