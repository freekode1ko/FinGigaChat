import json
import re

import pandas as pd
from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import config
from bot_logger import user_logger
from constants.bot.constants import CANCEL_CALLBACK
from database import engine
from utils.bot.base import user_in_whitelist
from module.mail_parse import ImapParse


# States
class Form(StatesGroup):
    permission_to_delete = State()
    send_to_users = State()
    new_user_reg = State()
    continue_user_reg = State()


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


@router.callback_query(F.data.startswith(CANCEL_CALLBACK))
async def cancel_callback(callback_query: types.CallbackQuery) -> None:
    """Удаляет сообщение, у которого нажали на отмену"""
    try:
        await callback_query.message.delete()
    except TelegramBadRequest:
        await callback_query.message.edit_text(text='Действие отменено', reply_markup=None)


@router.message(Command('addme'))
async def user_registration(message: types.Message, state: FSMContext):
    """
    Регистрация нового пользователя
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    if not await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : начал процесс регистрации')
        '''
        Надо добавить вывод сообщения: "Введите свою почту", там сделать проверку что это @sberbank.ru
        Если почта @sberbank.ru, то отправка закодированного chat_id на почту и ожидание сообщения от пользователя
            После ввода следующего сообщения раскодируем его и сверяем с chat_id сообщения, если ок - добавляем в бд,
            Если не сходится, то пишем что код не верный и просим проверить и повторить отправку
            Так до тех пор пока не получим правильный код.
        Если почта не @sberbank.ru, то сообщить что почта должна быть корпоративной и так пока не получим валидную почту
        
        По слову "отмена" - отменить регистрацию
        '''
        await state.set_state(Form.new_user_reg)
        await message.answer('Введите свою корпоративную почту для получения кода '
                             'необходимый для завершения регистрации')
    else:
        await message.answer(f'{full_name}, Вы уже наш пользователь!', protect_content=False)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : уже добавлен')


@router.message(Form.new_user_reg)
async def ask_user_mail(message: types.Message, state: FSMContext):
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    if re.search('\w+@sberbank.ru', user_msg.strip()):
        user_reg_code = chat_id  # TODO: Encrypt chat_id with key (static or dynamic?)
        imap_obj = ImapParse()
        imap_obj.send_msg(config.mail_username, config.mail_password, 'freekode1ko@gmail.com',  # Поменять на user_msg.strip()
                          config.reg_mail_text.format(user_reg_code))
        await state.clear()
        await state.set_state(Form.continue_user_reg)
        await message.answer(f'Введите код из конца письма, '
                             f'который был выслан вам на указанную почту ({user_msg.strip()})', protect_content=False)
    else:
        await message.answer(f'Не корректный ввод: {user_msg.strip()}', protect_content=False)


@router.message(Form.continue_user_reg)
async def validate_user_reg_code(message: types.Message, state: FSMContext):
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    if str(chat_id) == str(user_msg):
        user_raw = json.loads(message.from_user.model_dump_json())
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
            await state.clear()
        except Exception as e:
            await message.answer(f'Во время авторизации произошла ошибка, попробуйте позже. ' f'\n\n{e}', protect_content=False)
            user_logger.critical(f'*{chat_id}* {full_name} - {user_msg} : ошибка авторизации ({e})')
            await state.clear()
    else:
        await message.answer('Введен некорректный регистрационный код, проверьте написание и отправьте еще раз',
                             protect_content=False)
