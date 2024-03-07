import json

import pandas as pd
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from configs import config
from log.bot_logger import user_logger
from db.database import engine
from utils.bot.base import user_in_whitelist


# States
class Form(StatesGroup):
    permission_to_delete = State()
    send_to_users = State()


# logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('start', 'help'))
async def help_handler(message: types.Message) -> None:
    """
    Вывод приветственного окна, с описанием бота и лицами для связи

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    help_text = config.help_text
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        to_pin = await message.answer(help_text, protect_content=False)
        msg_id = to_pin.message_id
        await message.bot.pin_chat_message(chat_id=chat_id, message_id=msg_id)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


async def finish_state(message: types.Message, state: FSMContext, msg_text: str) -> None:
    """
    Позволяет пользователю очищать клавиатуру и выходить из любого состояния

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: состояние FSM
    :param msg_text: Ответное сообщение пользователю
    """
    if state is None:
        return

    # Cancel state and inform user about it
    await state.clear()
    # And remove keyboard (just in case)
    await message.reply(msg_text, reply_markup=types.ReplyKeyboardRemove())


@router.message(Command('exit', 'завершить'))
@router.message(F.text.lower().in_({'exit', 'завершить'}))
async def exit_handler(message: types.Message, state: FSMContext) -> None:
    await finish_state(message, state, 'Завершено')


@router.message(Command('cancel', 'отмена'))
@router.message(F.text.lower().in_({'cancel', 'отмена'}))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    await finish_state(message, state, 'Отменено')


@router.message(Command('addmetowhitelist'))
async def user_to_whitelist(message: types.Message):
    """
    Добавление нового пользователя в список на доступ

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    return None
    """
    user_raw = json.loads(message.from_user.model_dump_json())
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if not await user_in_whitelist(message.from_user.model_dump_json()):
        if 'username' in user_raw:
            user_username = user_raw['username']
        else:
            user_username = 'Empty_username'
        user_id = user_raw['id']
        user = pd.DataFrame(
            [[user_id, user_username, full_name, 'user', 'active', None]],
            columns=['user_id', 'username', 'full_name', 'user_type', 'user_status', 'subscriptions'],
        )
        try:
            user.to_sql('whitelist', if_exists='append', index=False, con=engine)
            await message.answer(f'Добро пожаловать, {full_name}!', protect_content=False)
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : новый пользователь')
        except Exception as e:
            await message.answer(f'Во время авторизации произошла ошибка, попробуйте позже. ' f'\n\n{e}', protect_content=False)
            user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : ошибка авторизации ({e})')
    else:
        await message.answer(f'{full_name}, Вы уже наш пользователь!', protect_content=False)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : уже добавлен')
