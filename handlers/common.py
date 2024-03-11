import json
import random
import re

import pandas as pd
from psycopg2.errors import UniqueViolation
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import config
from bot_logger import user_logger
from constants.bot.constants import CANCEL_CALLBACK
from database import engine
from module.mail_parse import SmtpSend
from utils.bot.base import user_in_whitelist

# from utils.data_crypto import AESCrypther


# States
class Form(StatesGroup):
    permission_to_delete = State()
    send_to_users = State()
    new_user_reg = State()
    continue_user_reg = State()


# logger = logging.getLogger(__name__)
router = Router()


@router.message(Command('start', 'help'))
async def help_handler(message: types.Message, state: FSMContext) -> None:
    """
    Вывод приветственного окна, с описанием бота и лицами для связи

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state:
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    if await user_in_whitelist(message.from_user.model_dump_json()):
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


async def user_registration(message: types.Message, state: FSMContext):
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
    if not await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : начал процесс регистрации')
        await state.set_state(Form.new_user_reg)
        new_user_start = config.new_user_start
        await message.answer(new_user_start, protect_content=False)
        # await message.answer('Введите корпоративную почту, на нее будет отправлен код для завершения регистрации')
    else:
        await message.answer(f'{full_name}, Вы уже наш пользователь!', protect_content=False)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : уже добавлен')


@router.message(Form.new_user_reg)
async def ask_user_mail(message: types.Message, state: FSMContext):
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    if (re.search('\w+@sberbank.ru', user_msg.strip())) or (re.search('\w+@sber.ru', user_msg.strip())):
        # TODO: оставить только 1 ключ и сократить количество знаков до 4-5
        user_reg_code_1 = str(chat_id + random.randint(1, 1000))[-4:]  # Генерация уникального кода № 1
        # user_reg_code_2 = str(AESCrypther(user_reg_code_1).encrypt(user_reg_code_1))  # Генерация уникального кода № 2

        # Отправка письма с регистрационными кодами (user_id (key1) и зашифрованный ключ (key2))
        SS = SmtpSend()  # TODO: Вынести в with открытие, отправку и закрытия
        SS.get_connection(config.mail_username, config.mail_password, config.mail_smpt_server, config.mail_smpt_port)
        SS.send_msg(
            config.mail_username,
            user_msg.strip(),
            config.mail_register_subject,
            config.reg_mail_text.format(user_reg_code_1),
        )
        SS.close_connection()

        await state.clear()
        await state.set_state(Form.continue_user_reg)
        await state.update_data(user_email=user_msg.strip(), user_reg_code=user_reg_code_1)
        await message.answer('Для завершения регистрации, введите код, отправленный вам на почту', protect_content=False)
    else:
        await message.answer('Указана не корпоративная почта', protect_content=False)
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Form.continue_user_reg)
async def validate_user_reg_code(message: types.Message, state: FSMContext):
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text.strip()
    user_reg_info = await state.get_data()
    # try:
    #     user_reg_code = AESCrypther(str(user_reg_info['user_reg_code'])).decrypt(user_msg.encode('utf-8'))
    #     user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : {user_reg_code}')
    # except ValueError:
    #     '''
    #     Я забыл что с коп. почты на телефоне нельзя скопировать текст письма, так что добавим
    #     проверку user_msg на схожесть с chat_id и отправим его вместе с закодированным
    #     '''
    #     user_reg_code = 'ERROR_USER_CODE'
    #     if user_msg == str(user_reg_info['user_reg_code']):
    #         user_reg_code = user_msg
    user_reg_code = user_msg
    if str(user_reg_info['user_reg_code']) == str(user_reg_code):

        user_raw = json.loads(message.from_user.model_dump_json())
        if 'username' in user_raw:
            user_username = user_raw['username']
        else:
            user_username = 'Empty_username'
        user_id = user_raw['id']
        user_email = user_reg_info['user_email']
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
            if isinstance(e.orig, UniqueViolation):
                update_user_mail(user_id, user_email)
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
        await message.answer('Введен некорректный регистрационный код', protect_content=False)
        user_logger.critical(f'*{chat_id}* {full_name} - {user_msg}. Обработчик кода ответил: {user_reg_code}')


def update_user_mail(user_id: int, user_email: str):
    """Обновление почты существующего пользователя"""
    query = text('UPDATE whitelist SET user_email=:user_email WHERE user_id=:user_id')
    with engine.connect() as conn:
        conn.execute(query.bindparams(user_email=user_email, user_id=user_id))
        conn.commit()
