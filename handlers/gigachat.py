# import logging

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware

import module.gigachat as gig
from bot_logger import logger, user_logger
from constants.bot.constants import giga_ans_footer
from utils.bot_utils import user_in_whitelist

token = ''
chat = ''

# logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


class GigaChat(StatesGroup):
    gigachat_mode = State()


@router.message(Command('gigachat'))
async def set_gigachat_mode(message: types.Message, state: FSMContext) -> None:
    """
    Переключение в режим общения с Gigachat

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    if await user_in_whitelist(message.from_user.model_dump_json()):
        await state.set_state(GigaChat.gigachat_mode)

        cancel_command = 'завершить'
        cancel_msg = f'Напишите «{cancel_command}» для завершения общения с Gigachat'
        msg_text = 'Начато общение с Gigachat\n\n' + cancel_msg
        buttons = [[types.KeyboardButton(text=cancel_command)]]

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True, input_field_placeholder=cancel_msg, one_time_keyboard=True
        )
        await message.answer(msg_text, reply_markup=keyboard)
    else:
        chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


# @dp.message(F.text.lower().startswith('askgigachat') | F.text.lower().startswith('спросить'))
@router.message(GigaChat.gigachat_mode)
async def ask_giga_chat(message: types.Message, prompt: str = '') -> None:
    """Отправка пользователю ответа, сформированного Gigachat, на сообщение пользователя"""

    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    global chat
    global token
    msg = f'{prompt} {message.text}'
    msg = msg.replace('/bonds', '')
    msg = msg.replace('/eco', '')
    msg = msg.replace('/commodities', '')
    msg = msg.replace('/fx', '')

    try:
        giga_answer = chat.ask_giga_chat(token=token, text=msg)
        giga_js = giga_answer.json()['choices'][0]['message']['content']
    except AttributeError:
        chat = gig.GigaChat()
        token = chat.get_user_token()
        logger.debug(f'*{chat_id}* {full_name} : перевыпуск токена для общения с GigaChat')
        giga_answer = chat.ask_giga_chat(token=token, text=msg)
        giga_js = giga_answer.json()['choices'][0]['message']['content']
    except KeyError:
        chat = gig.GigaChat()
        token = chat.get_user_token()
        logger.debug(f'*{chat_id}* {full_name} : перевыпуск токена для общения с GigaChat')
        giga_answer = chat.ask_giga_chat(token=token, text=msg)
        giga_js = giga_answer.json()['choices'][0]['message']['content']
        user_logger.critical(
            f'*{chat_id}* {full_name} - {user_msg} :'
            f' KeyError (некорректная выдача ответа GigaChat),'
            f' ответ после переформирования запроса'
        )
    response = f'{giga_js}\n\n{giga_ans_footer}'
    try:
        await message.answer(response, protect_content=False)
    except Exception as e:
        logger.error(f'ERROR: {e}')

    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}" : На запрос GigaChat ответил: "{giga_js}"')
