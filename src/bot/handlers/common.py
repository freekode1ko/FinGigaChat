"""
Описание общих обработчиков событий в боте.

    Содержит методы по:
        выводу информационного сообщения о боте
        регистрации пользователя в боте
        по выходу из состояния
        открытию web app с календарем (встречами)
"""
import json
import random
import re

from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types.web_app_info import WebAppInfo
from sqlalchemy.ext.asyncio import AsyncSession

from configs import config
from constants.constants import (
    CANCEL_CALLBACK,
    MAX_REGISTRATION_CODE_ATTEMPTS,
    REGISTRATION_CODE_MAX,
    REGISTRATION_CODE_MIN,
)
from constants.texts import texts_manager
from db.user import insert_user_email_after_register, is_new_user_email, is_user_email_exist
from db.whitelist import is_email_in_whitelist
from handlers.ai.rag.rag import clear_user_dialog_if_need
from log.bot_logger import user_logger
from module.email_send import SmtpSend
from utils.base import is_user_has_access


class Form(StatesGroup):
    """Конечный автомат состояний регистрации пользователя."""

    new_user_reg = State()
    continue_user_reg = State()


router = Router()


@router.message(Command('start', 'help'))
async def help_handler(message: types.Message, state: FSMContext) -> None:
    """Вывод приветственного окна, с описанием бота и лицами для связи."""
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    check_mail = user_msg == '/start'
    if await is_user_has_access(message.from_user.model_dump_json(), check_mail):
        help_text = config.help_text
        to_pin = await message.answer(help_text, protect_content=texts_manager.PROTECT_CONTENT)
        msg_id = to_pin.message_id
        await message.bot.pin_chat_message(chat_id=chat_id, message_id=msg_id)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
        await user_registration(message, state)


async def finish_state(message: types.Message, state: FSMContext, msg_text: str) -> None:
    """
    Позволяет пользователю очищать клавиатуру и выходить из любого состояния.

    :param message:     Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param state:       Состояние FSM.
    :param msg_text:    Ответное сообщение пользователю.
    """
    if state is None:
        return

    await clear_user_dialog_if_need(message, state)  # очистка истории диалога, если состояние RagState
    await state.clear()
    await message.reply(msg_text, reply_markup=types.ReplyKeyboardRemove())


@router.message(Command('exit', 'завершить'))
@router.message(F.text.lower().in_({'exit', 'завершить'}))
async def exit_handler(message: types.Message, state: FSMContext) -> None:
    """Вызов метода по выходу из состояния."""
    await finish_state(message, state, 'Завершено')


@router.message(Command('cancel', 'отмена'))
@router.message(F.text.lower().in_({'cancel', 'отмена'}))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """Вызов метода по выходу из состояния."""
    await finish_state(message, state, 'Отменено')


@router.callback_query(F.data.startswith(CANCEL_CALLBACK))
async def cancel_callback(callback_query: types.CallbackQuery) -> None:
    """Удаляет сообщение, у которого нажали на отмену."""
    try:
        await callback_query.message.delete()
    except TelegramBadRequest:
        await callback_query.message.edit_text(text='Действие отменено', reply_markup=None)


async def user_registration(message: types.Message, state: FSMContext) -> None:
    """Регистрация нового пользователя в боте: запрос пользовательской почты."""
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : начал процесс регистрации')
    await state.set_state(Form.new_user_reg)
    new_user_start = config.new_user_start
    await message.answer(new_user_start, protect_content=texts_manager.PROTECT_CONTENT)


@router.message(Form.new_user_reg)
async def ask_user_mail(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """
    Обработка пользовательской почты и отправка регистрационного кода на нее.

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state:   Состояние FSM
    :param session: Асинхронная сессия базы данных.
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text.strip().lower()
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    if re.search(r'\w+@sber(bank)?.ru', user_msg):
        # проверка на существования пользователя с введенной почтой
        if not is_new_user_email(user_msg):
            await state.clear()
            await message.answer('Пользователь с такой почтой уже существует! '
                                 'Нажмите /start, чтобы попробовать еще раз.')
            user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : при регистрации использовалась чужая почта')
            return
        elif not (await is_email_in_whitelist(session, user_msg)):
            await state.clear()
            await message.answer('Для продолжения регистрации, пожалуйста, свяжитесь с командой проекта: @korolkov_m')
            user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : '
                                 f'попытка регистрации пользователя, отсутствующего в белом списке')
            return

        reg_code = str(random.randint(REGISTRATION_CODE_MIN, REGISTRATION_CODE_MAX))  # генерация уникального кода

        with SmtpSend(config.MAIL_RU_LOGIN, config.MAIL_RU_PASSWORD, config.mail_smpt_server, config.mail_smpt_port) as smtp_email:

            smtp_email.send_msg(
                config.MAIL_RU_LOGIN,
                user_msg,
                config.mail_register_subject,
                config.reg_mail_text.format(reg_code),
            )
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : '
                             f'код для регистрации отправлен на почту {user_msg}')

        await state.clear()
        await state.set_state(Form.continue_user_reg)
        await state.update_data(
            user_email=user_msg,
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
    """Валидация введенного пользователем регистрационного кода и добавление пользователя в БД."""
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

        welcome_msg = f'Добро пожаловать, {full_name}!'
        exc_msg = 'Во время авторизации произошла ошибка, попробуйте позже.'
        try:
            await insert_user_email_after_register(user_id, user_username, full_name, user_email)
            await message.answer(welcome_msg)
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : новый пользователь')
            await help_handler(message, state)
        except Exception as e:
            await message.answer(exc_msg)
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


@router.message(Command('meeting'))
async def open_meeting_app(message: types.Message) -> None:
    """Открытие веб приложения со встречами."""
    user_id = message.from_user.id
    if not is_user_email_exist(user_id):
        await message.answer('Для работы со встречами необходимо пройти регистрацию: /start')
        return

    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text='Мои встречи', web_app=WebAppInfo(url=f'{config.WEB_APP_URL}/meeting/show'))],
        ],
        resize_keyboard=True
    )
    await message.answer('Для работы со встречами нажмите:', reply_markup=markup)
