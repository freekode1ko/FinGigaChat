
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware

import module.gigachat as gig
from bot_logger import logger, user_logger
from constants.bot.constants import giga_ans_footer
from utils.bot.base import user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'
chat = gig.GigaChat(logger)


class GigaChatState(StatesGroup):
    gigachat_mode = State()
    gigachat_query = State()


@router.message(Command('gigachat'))
async def set_gigachat_mode(message: types.Message, state: FSMContext) -> None:
    """
    Переключение в режим общения с Gigachat

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
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
    """Отправка пользователю ответа, сформированного Gigachat, на сообщение пользователя"""
    await ask_giga_chat(message)


async def ask_giga_chat(message: types.Message, first_user_query: str = '') -> None:
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    await message.bot.send_chat_action(message.chat.id, 'typing')
    response = route_query(chat_id, full_name, first_user_query if first_user_query else user_msg)
    await message.answer(response, protect_content=False)

    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : На запрос GigaChat ответил: "{response}"')


def route_query(chat_id: int, full_name: str, user_msg: str):
    """
    Будущая маршрутизация рага(ов) и запросов к гиге
    Будет изменяться
    """

    try:
        giga_answer = chat.get_giga_answer(text=user_msg)
    except Exception as e:
        logger.error(f'ERROR : GigaChat не сформировал ответ по причине: {e}"')
        user_logger.error(f'*{chat_id}* {full_name} - "{user_msg}" : GigaChat не сформировал ответ по причине: {e}"')
        giga_answer = 'Извините, я пока не могу ответить на ваш запрос'

    response = f'{giga_answer}\n\n{giga_ans_footer}'
    return response

