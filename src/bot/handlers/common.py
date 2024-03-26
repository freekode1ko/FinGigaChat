import json
import random
import re

import pandas as pd
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from configs import config
from log.bot_logger import user_logger
from constants.constants import (
    CANCEL_CALLBACK,
    MAX_REGISTRATION_CODE_ATTEMPTS,
    REGISTRATION_CODE_MIN,
    REGISTRATION_CODE_MAX,
)
from db.database import engine
from module.mail_parse import SmtpSend
from utils.base import user_in_whitelist
from db.whitelist import update_user_email, is_new_user_email


# States
class Form(StatesGroup):
    permission_to_delete = State()
    send_to_users = State()
    new_user_reg = State()
    continue_user_reg = State()


router = Router()


@router.message(Command('start', 'help'))
async def help_handler(message: types.Message, state: FSMContext) -> None:
    """
    Вывод приветственного окна, с описанием бота и лицами для связи

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state:
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    check_mail = user_msg == '/start'
    if await user_in_whitelist(message.from_user.model_dump_json(), check_mail):
        help_text = config.help_text
        to_pin = await message.answer(help_text, protect_content=False)
        msg_id = to_pin.message_id
        await message.bot.pin_chat_message(chat_id=chat_id, message_id=msg_id)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
        await user_registration(message, state)


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


@router.callback_query(F.data.startswith(CANCEL_CALLBACK))
async def cancel_callback(callback_query: types.CallbackQuery) -> None:
    """Удаляет сообщение, у которого нажали на отмену"""
    try:
        await callback_query.message.delete()
    except TelegramBadRequest:
        await callback_query.message.edit_text(text='Действие отменено', reply_markup=None)


async def user_registration(message: types.Message, state: FSMContext) -> None:
    """
    Регистрация нового пользователя.
    Если почта \\w+@sberbank.ru, то отправка закодированного chat_id на почту и ожидание сообщения от пользователя
        После ввода следующего сообщения раскодируем его и сверяем с chat_id сообщения, если ок - добавляем в БД,
        Если не сходится, то пишем что код не верный и просим проверить и повторить отправку
        Так до тех пор, пока не получим правильный код.
    Если почта не \\w+@sberbank.ru, то сообщить что почта должна быть корпоративной и так пока не получим валидную почту

    По слову "отмена" в чате - отменить регистрацию
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : начал процесс регистрации')
    await state.set_state(Form.new_user_reg)
    new_user_start = config.new_user_start
    await message.answer(new_user_start, protect_content=False)


@router.message(Form.new_user_reg)
async def ask_user_mail(message: types.Message, state: FSMContext) -> None:
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text.strip()
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    if (re.search(r'\w+@sberbank.ru', user_msg)) or (re.search(r'\w+@sber.ru', user_msg)):
        # проверка на существования пользователя с введенной почтой
        if not is_new_user_email(user_msg):
            await state.clear()
            await message.answer('Пользователь с такой почтой уже существует! Нажмите /start, чтобы попробовать еще раз.')
            user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : при регистрации использовалась чужая почта')
            return

        reg_code = str(random.randint(REGISTRATION_CODE_MIN, REGISTRATION_CODE_MAX))  # генерация уникального кода
        SS = SmtpSend()  # TODO: Вынести в with открытие, отправку и закрытия
        SS.get_connection(config.mail_username, config.mail_password, config.mail_smpt_server, config.mail_smpt_port)
        SS.send_msg(
            config.mail_username,
            user_msg.strip(),
            config.mail_register_subject,
            config.reg_mail_text.format(reg_code),
        )
        SS.close_connection()

        await state.clear()
        await state.set_state(Form.continue_user_reg)
        await state.update_data(
            user_email=user_msg.strip(),
            reg_code=reg_code,
            attempts_left=MAX_REGISTRATION_CODE_ATTEMPTS
        )
        await message.answer('Для завершения регистрации, введите код, отправленный вам на почту.')
    else:
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text='отмена')], ],
            resize_keyboard=True,
            input_field_placeholder='Введите корпоративную почту',
            one_time_keyboard=True
        )
        await message.answer('Указана не корпоративная почта', reply_markup=keyboard)
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Form.continue_user_reg)
async def validate_user_reg_code(message: types.Message, state: FSMContext) -> None:
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text.strip()
    reg_info = await state.get_data()
    reg_code: str = reg_info['reg_code']

    if reg_code == user_msg:
        user_raw = json.loads(message.from_user.model_dump_json())
        if 'username' in user_raw:
            user_username = user_raw['username']
        else:
            user_username = 'Empty_username'
        user_id = user_raw['id']
        user_email = reg_info['user_email']
        user = pd.DataFrame(
            [[user_id, user_username, full_name, 'user', 'active', None, user_email]],
            columns=['user_id', 'username', 'full_name', 'user_type', 'user_status', 'subscriptions', 'user_email'])

        welcome_msg = f'Добро пожаловать, {full_name}!'
        exc_msg = 'Во время авторизации произошла ошибка, попробуйте позже.\n\n{exc}'
        try:
            user.to_sql('whitelist', if_exists='append', index=False, con=engine)
            await message.answer(welcome_msg)
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : новый пользователь')
            await help_handler(message, state)

        except IntegrityError as e:
            # если пользователь уже есть в системе, обновляем ему почту
            if isinstance(e.orig, UniqueViolation):
                update_user_email(user_id, user_email)
                await message.answer(welcome_msg)
                user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : пользователь обновил почту')
            else:
                await message.answer(exc_msg.format(exc=e))
                user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : ошибка авторизации ({e})')

        except Exception as e:
            await message.answer(exc_msg.format(exc=e))
            user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : ошибка авторизации ({e})')

        finally:
            await state.clear()

    else:
        attempts_left = reg_info['attempts_left'] - 1
        if not attempts_left:
            await state.clear()
            await message.answer('Вы истратили все попытки. Попробуйте заново, используя команду /start.')
            user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : неуспешная регистрация')
            return

        await state.update_data(attempts_left=attempts_left)
        await message.answer(f'Вы ввели некорректный регистрационный код. Осталось {attempts_left} попытки.')
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : пользователь ввел некорректный код, '
                            f'нужный код: {reg_code}, осталось попыток: {attempts_left}.')
