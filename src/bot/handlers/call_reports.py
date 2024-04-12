import os
import subprocess
from datetime import datetime
from typing import Optional

import requests
import speech_recognition as sr
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import text

from configs import config
from log.bot_logger import logger
from db.database import engine
from module.mail_parse import SmtpSend
from utils.base import user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())


class CallReportsStates(StatesGroup):
    enter_clint_name = State()
    enter_date = State()
    enter_text_message = State()
    final_check = State()


def validate_and_parse_date(date_str: str) -> Optional[datetime.date]:
    """
    Валидация строки с датой и возвращение ее в datetime object
    :param date_str: date str
    """
    try:
        date_obj = datetime.strptime(date_str, config.BASE_DATE_FORMAT)
        return date_obj.date()
    except ValueError:
        return


async def audio_to_text(message: types.Message,) -> str:
    """
    Превращает аудио сообщение в текст

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :return: строку полученную из аудио сообщения
    """
    try:
        logger.info(f'Call Report: Start audio_to_text for user id: {message.chat.id}')
        file_id = message.voice.file_id
        audio_file = await message.bot.get_file(file_id)

        audio_file_url = f"https://api.telegram.org/file/bot{config.api_token}/{audio_file.file_path}"
        req = requests.get(audio_file_url)
        path_to_file_oga = config.TMP_VOICE_FILE_DIR / f'{file_id}.oga'

        with open(path_to_file_oga, 'wb') as f:
            f.write(req.content)

        path_to_file_wav = config.TMP_VOICE_FILE_DIR / f'{file_id}.wav'

        process = subprocess.run(['ffmpeg', '-i', str(path_to_file_oga), str(path_to_file_wav)])

        r = sr.Recognizer()
        voice_message = sr.AudioFile(str(path_to_file_wav))
        with voice_message as source:
            audio = r.record(source)
        try:
            result = r.recognize_google(audio, language="ru_RU")
            logger.info(f'Call Report: Успешная обработка аудио через гугл для {message.chat.id}')
        except Exception as e:
            logger.error(f'Call Report: Не успешная обработка аудио через гугл для {message.chat.id} из-за {e}')
            result = r.recognize_whisper(audio, model=config.WHISPER_MODEL, language="ru")
            logger.info(f'Call Report: Успешная обработка аудио через whisper для {message.chat.id}')
    except Exception as e:
        logger.error(f'Call Report: Не успешная обработка аудио для {message.chat.id} из-за {e}')
    finally:
        os.remove(path_to_file_wav)
        os.remove(path_to_file_oga)
        logger.info(f'Call Report: Успешная обработка аудио для {message.chat.id}')
        return result


@router.message(Command('call_reports'))
async def call_reports(message: types.Message, state: FSMContext) -> None:
    """
    Входная точка для создания или просмотра кол репортов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    await state.clear()
    if await user_in_whitelist(message.from_user.model_dump_json()):
        logger.info(f'Call Report: Страт call reports для {str(message.chat.id)}')
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            types.InlineKeyboardButton(text='Создать новый протокол встречи', callback_data='call_reports:create_new'))
        keyboard.row(
            types.InlineKeyboardButton(text='Посмотреть мои протоколы', callback_data='call_reports:my_reports'))

        await message.answer(
            'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?',
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(F.data.startswith('call_reports:create_new'))
async def call_reports_handler_create_new(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обработка кнопки для создания нового кол репорта

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Нажали на конпу создания нового call report для {callback_query.message.chat.id}')
    await callback_query.message.answer(
        'Вы перешли в режим записи протокола встречи с клиентом следуйте инструкциям, чтобы завершить процесс.',
    )
    await callback_query.message.answer(
        'Пожалуйста, не включайте в отчет конфиденциальную информацию',
    )
    await callback_query.message.answer(
        'Введите, пожалуйста, Клиента, с кем проходила встреча:',
    )
    await state.set_state(CallReportsStates.enter_clint_name)


@router.callback_query(F.data.startswith('call_reports:my_reports'))
async def call_reports_handler_my_reports(callback_query: types.CallbackQuery, state: FSMContext) -> None: # TODO: добавить список кол репортов
    """
    Обработка кнопок по получению списка уже созданных кол репортов

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Нажали на конпу получения списка call report для {callback_query.message.chat.id}')
    await callback_query.message.answer(
        'Данный функционал будет позже',
    )


@router.callback_query(F.data.startswith('call_reports:send_to_mail'))
async def call_reports_handler_send_to_mail(callback_query: types.CallbackQuery,
                                          state: FSMContext) -> None:
    """
    Обработка кнопок отправки на почту кол репорта

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Нажали на конпу отправки на почту report для {callback_query.message.chat.id}')
    state_data = await state.get_data()
    user_id = callback_query.message.chat.id
    client = state_data.get("client", None)
    date = state_data.get("date", None)
    report = state_data.get("text", None)


    with engine.connect() as conn:
        data = conn.execute(
            text(
                f'SELECT user_email FROM whitelist WHERE  user_id={user_id}'
            )
        ).fetchone()
        user_email = data[0]

    try:
        logger.info(f'Call Report: Начало отправки на почту report для {callback_query.message.chat.id}')
        SS = SmtpSend()  # TODO: Вынести в with открытие, отправку и закрытия
        SS.get_connection(config.mail_username, config.mail_password, config.mail_smpt_server, config.mail_smpt_port)
        SS.send_msg(
            config.mail_username,
            user_email,
            f'Протокол Встречи: {client} {date}',
            (
                f'Клиент: {client}\n'
                f'Дата: {date}\n'
                f'Запись встречи: {report}\n'
            ),
        )
        SS.close_connection()
        await callback_query.message.answer(
            f'Протокол на почту {user_email} отправлен',
        )
    except Exception as e:
        logger.error(f'Call Report: Письмо не отправлено на почту report для {callback_query.message.chat.id} из-за {e}')
    finally:
        logger.info(f'Call Report: Письмо успешно отправлено на почту report для {callback_query.message.chat.id}')

    try:
        logger.info(f'Call Report: Сохранение call report для {callback_query.message.chat.id}')
        with engine.connect() as conn:
            query = text(
                f'INSERT INTO bot_call_reports (user_id, client, report_date, description) '
                'VALUES (:user_id, :client, :date, :report) '
            )

            data = conn.execute(query)
            conn.commit()
    except Exception as e:
        logger.error(f'Call Report: Сохранение call report не удалось для {callback_query.message.chat.id} из-за {e}')
    finally:
        logger.info(f'Call Report: Успешное сохранение call report для {callback_query.message.chat.id}')



@router.message(CallReportsStates.enter_clint_name)
async def enter_clint_name(message: types.Message, state: FSMContext) -> None:
    """
    Обработка клиента, который ввел пользователь для создания кол репорта

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Сохранение клиента в call report для {message.chat.id}')
    if True:  # FIXME В дальнейшем будет браться из таблицы в БД
        await message.answer(
            'Укажите дату встречи в формате ДД.ММ.ГГГГ:',
        )
        await state.set_state(CallReportsStates.enter_date)
        await state.update_data(
            client=message.text,
        )


@router.message(CallReportsStates.enter_date)
async def enter_date(message: types.Message, state: FSMContext) -> None:
    """
    Обработка даты, который ввел пользователь для создания кол репорта

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Сохранение даты в call report для {message.chat.id}')
    if date := validate_and_parse_date(message.text):
        await message.answer(
            'Запишите основные моменты встречи(Голосом или текстом)',
        )
        await state.set_state(CallReportsStates.enter_text_message)
        await state.update_data(
            date=date,
        )
    else:
        await message.answer(
            'Кажется, дата введена некорректно.\nУбедитесь, что вы используете формат ДД.ММ.ГГГГ и попробуйте еще раз:',
        )
    logger.info(f'Call Report: Конец сохранения даты в call report для {message.chat.id}')

@router.message(CallReportsStates.enter_text_message, F.content_type.in_({'voice', 'text',}), )
async def enter_text_message(message: types.Message, state: FSMContext) -> None:
    """
      Обработка текста/аудио, который ввел пользователь для создания кол репорта

      :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
      :param state: Объект, который хранит состояние FSM для пользователя
      """
    logger.info(f'Call Report: Сохранения текста/аудио в call report для {message.chat.id}')

    if message.voice:
        result = await audio_to_text(message)
    else:
        result = message.text

    await state.update_data(
        text=result,
    )
    data = await state.get_data()

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(text='Отправить на почту', callback_data='call_reports:send_to_mail'))
    await message.answer(
        (
            'Все готово! Проверьте введенные данные:\n'
            f'Клиент: {data.get("client", None)}\n'
            f'Дата: {data.get("date", None)}\n'
            f'Запись встречи: {result}\n'
            '\n'
            'Если все верно, нажмите кнопку "Отправить на почту" для завершения процесса.'
        ),
        reply_markup=keyboard.as_markup(),
    )
    logger.info(f'Call Report: Конец сохранения текста/аудио в call report для {message.chat.id}')
