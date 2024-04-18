import copy
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
from sqlalchemy import text, select, update

from configs import config
from db.database import engine, async_session
from db.models import CallReports
from handlers.call_reports import keyboards
from handlers.call_reports.callbackdata import CallReportsCallbackData, CallReportsMenus
from log.bot_logger import logger
from module.email_send import SmtpSend
from src.web_app.db.models import Whitelist
from utils.base import user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())

emoji = copy.deepcopy(config.dict_of_emoji)
MAX_CALUES_PER_PAGE = 10


class CallReportsStates(StatesGroup):
    enter_clint_name = State()
    enter_date = State()
    enter_text_message = State()
    final_check = State()


class CallReportsEditStates(StatesGroup):
    edit_clint_name = State()
    edit_date = State()
    edit_text_message = State()


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


async def audio_to_text(message: types.Message, ) -> str:
    """
    Превращает аудио сообщение в текст

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :return: строку полученную из аудио сообщения
    """
    result = ''
    path_to_file_oga = ''
    path_to_file_wav = ''

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
        if path_to_file_wav and os.path.exists(path_to_file_wav):
            os.remove(path_to_file_wav)
        if path_to_file_oga and os.path.exists(path_to_file_oga):
            os.remove(path_to_file_oga)
        logger.info(f'Call Report: Успешная обработка аудио для {message.chat.id}')
        return result


async def send_to_mail(user_email, client, date, report):
    with SmtpSend(
            config.MAIL_RU_LOGIN,
            config.MAIL_RU_PASSWORD,
            config.mail_smpt_server,
            config.mail_smpt_port
    ) as SS:
        SS.send_msg(
            config.MAIL_RU_LOGIN,
            user_email,
            f'Протокол Встречи: {client} {date.strftime(config.BASE_DATE_FORMAT)}',
            (
                f'Клиент: {client}\n'
                f'Дата: {date.strftime(config.BASE_DATE_FORMAT)}\n'
                f'Запись встречи: {report}\n'
            ),
        )


async def main_menu(message: types.Message, edit: bool = False) -> None:
    logger.info(f'Call Report: Страт call reports для {str(message.chat.id)}')
    keyboard = keyboards.main_menu_keyboard()

    if edit:
        await message.edit_text(
            'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?',
            reply_markup=keyboard.as_markup(),
        )
    else:
        await message.answer(
            'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?',
            reply_markup=keyboard.as_markup(),
        )


@router.message(Command('call_reports'))
async def call_reports_command(message: types.Message, state: FSMContext, ) -> None:
    """
    Входная точка для создания или просмотра кол репортов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    await state.clear()
    if await user_in_whitelist(message.from_user.model_dump_json()):
        await main_menu(message)


@router.callback_query(CallReportsCallbackData.filter(F.menu == CallReportsMenus.main))
async def call_reports_main_menu(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
) -> None:
    """
    Входная точка для создания или просмотра кол репортов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    await main_menu(callback_query.message, True)


@router.callback_query(CallReportsCallbackData.filter(F.menu == CallReportsMenus.close))
async def call_reports_close(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
) -> None:
    """
    Входная точка для создания или просмотра кол репортов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    await callback_query.message.delete()


@router.callback_query(CallReportsCallbackData.filter(F.menu == CallReportsMenus.create_new))
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


@router.callback_query(CallReportsCallbackData.filter(F.menu == CallReportsMenus.send_to_mail_from_state))
async def call_reports_handler_send_to_mail_from_state(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Обработка кнопок отправки на почту кол репорта

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Нажали на конпу отправки на почту report для {callback_query.message.chat.id}')
    await callback_query.message.edit_reply_markup(None)

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

        await send_to_mail(user_email, client, date, report)

        answer_text = f'Протокол на почту {user_email} отправлен'

        await callback_query.message.answer(
            answer_text,
            reply_markup=keyboards.main_menu_keyboard().as_markup()
        )
        await callback_query.answer(answer_text)

        await state.clear()
    except Exception as e:
        logger.error(
            f'Call Report: Письмо не отправлено на почту report для {callback_query.message.chat.id} из-за {e}')
    finally:
        logger.info(f'Call Report: Письмо успешно отправлено на почту report для {callback_query.message.chat.id}')

    try:
        logger.info(f'Call Report: Сохранение call report для {callback_query.message.chat.id}')
        with engine.connect() as conn:
            query = text(
                'INSERT INTO bot_call_reports (user_id, client, report_date, description) '
                'VALUES (:user_id, :client, :date, :report) '
            )

            conn.execute(query.bindparams(user_id=user_id, client=client, date=date, report=report))
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


@router.message(CallReportsStates.enter_text_message, F.content_type.in_({'voice', 'text'}), )
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
        types.InlineKeyboardButton(
            text='Отправить на почту',
            callback_data=CallReportsCallbackData(menu=CallReportsMenus.send_to_mail_from_state).pack()),
    )
    await message.answer(
        (
            'Все готово! Проверьте введенные данные:\n'
            f'Клиент: {data.get("client", None)}\n'
            f'Дата: {data.get("date", None).strftime(config.BASE_DATE_FORMAT)}\n'
            f'Запись встречи: {result}\n'
            '\n'
            'Если все верно, нажмите кнопку "Отправить на почту" для завершения процесса.'
        ),
        reply_markup=keyboard.as_markup(),
    )
    logger.info(f'Call Report: Конец сохранения текста/аудио в call report для {message.chat.id}')


@router.callback_query(
    CallReportsCallbackData.filter(F.menu == CallReportsMenus.my_reports),
    CallReportsCallbackData.filter(F.client == None)
)
async def call_reports_handler_my_reports(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
) -> None:
    """
    Базовое меню просмотров кол репортов

    :param callback_data: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    clients = None
    async with async_session() as session:
        clients = await session.execute(
            select(CallReports.client).filter(CallReports.user_id == callback_query.message.chat.id).distinct()
        )
        clients = [_[0] for _ in clients.fetchall()]

    if not clients:
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            types.InlineKeyboardButton(
                text='Создать новый протокол встречи',
                callback_data=CallReportsCallbackData(menu=CallReportsMenus.create_new).pack()
            )
        )
        keyboard.row(
            types.InlineKeyboardButton(
                text='Назад',
                callback_data=CallReportsCallbackData(menu=CallReportsMenus.main).pack()
            )
        )
        await callback_query.message.edit_text(
            'Похоже у вас еще нет протоколов встреч',
            reply_markup=keyboard.as_markup(),
        )
    else:
        keyboard = InlineKeyboardBuilder()
        for client in clients[callback_data.page * MAX_CALUES_PER_PAGE: (callback_data.page + 1) * MAX_CALUES_PER_PAGE]:
            keyboard.row(
                types.InlineKeyboardButton(
                    text=f'{client}',
                    callback_data=CallReportsCallbackData(
                        menu=CallReportsMenus.my_reports,
                        client=client,
                    ).pack()
                )
            )
        keyboard_footer = []
        if callback_data.page > 0:
            keyboard_footer.append(
                types.InlineKeyboardButton(
                    text=f'{emoji["backward"]}',
                    callback_data=CallReportsCallbackData(
                        menu=CallReportsMenus.my_reports,
                        client=None,
                        page=callback_data.page - 1,
                    ).pack()
                )
            )
        keyboard_footer.append(
            types.InlineKeyboardButton(
                text='Назад',
                callback_data=CallReportsCallbackData(menu=CallReportsMenus.main).pack()
            )
        )
        if len(clients) > (callback_data.page + 1) * MAX_CALUES_PER_PAGE:
            keyboard_footer.append(
                types.InlineKeyboardButton(
                    text=f'{emoji["forward"]}',
                    callback_data=CallReportsCallbackData(
                        menu=CallReportsMenus.my_reports,
                        client=None,
                        page=callback_data.page + 1,
                    ).pack()
                )
            )
        keyboard.row(*keyboard_footer)
        await callback_query.message.edit_text(
            'Существующие протоколы встреч:',
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(
    CallReportsCallbackData.filter(F.menu == CallReportsMenus.my_reports),
    CallReportsCallbackData.filter(F.client != None),
    CallReportsCallbackData.filter(F.call_report_id == 0),
)
async def call_reports_handler_my_reports_client(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
) -> None:
    async with async_session() as session:
        client_call_reports_dates = await session.execute(
            select(CallReports.id, CallReports.report_date).filter(
                CallReports.user_id == callback_query.message.chat.id,
                CallReports.client == callback_data.client,
            )
            .distinct()
        )
        client_call_reports_dates = client_call_reports_dates.fetchall()
    keyboard = InlineKeyboardBuilder()
    for call_report_id, date in client_call_reports_dates[
                                callback_data.page_date * MAX_CALUES_PER_PAGE:
                                (callback_data.page_date + 1) * MAX_CALUES_PER_PAGE]:
        # Просмотр колл репорта по дате
        keyboard.row(
            types.InlineKeyboardButton(
                text=f'{date.strftime(config.BASE_DATE_FORMAT)}',
                callback_data=CallReportsCallbackData(
                    menu=CallReportsMenus.my_reports,
                    client=callback_data.client,
                    call_report_id=call_report_id,
                    page=callback_data.page,
                    page_date=callback_data.page_date,
                ).pack()
            )
        )

    keyboard_footer = []
    if callback_data.page_date > 0:
        keyboard_footer.append(
            types.InlineKeyboardButton(
                text=f'{emoji["backward"]}',
                callback_data=CallReportsCallbackData(
                    menu=CallReportsMenus.my_reports,
                    client=callback_data.client,
                    page=callback_data.page,
                    page_date=callback_data.page_date - 1,
                ).pack()
            )
        )
    keyboard_footer.append(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data=CallReportsCallbackData(
                menu=CallReportsMenus.my_reports,
                page=callback_data.page,
            ).pack()
        )
    )
    if len(client_call_reports_dates) > (callback_data.page + 1) * MAX_CALUES_PER_PAGE:
        keyboard_footer.append(
            types.InlineKeyboardButton(
                text=f'{emoji["forward"]}',
                callback_data=CallReportsCallbackData(
                    menu=CallReportsMenus.my_reports,
                    client=callback_data.client,
                    page=callback_data.page,
                    page_date=callback_data.page_date + 1,
                ).pack()
            )
        )
    keyboard.row(*keyboard_footer)

    await callback_query.message.edit_text(
        f'Протокол встречи для клиента: "{callback_data.client}"',
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(
    CallReportsCallbackData.filter(F.menu == CallReportsMenus.my_reports),
    CallReportsCallbackData.filter(F.client != None),
    CallReportsCallbackData.filter(F.call_report_id != 0),
)
async def call_reports_handler_my_report(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
) -> None:
    async with async_session() as session:
        client_call_reports_dates = await session.execute(
            select(CallReports.client, CallReports.report_date, CallReports.description).filter(
                CallReports.id == callback_data.call_report_id,
            )
        )
        client, report_date, description = client_call_reports_dates.fetchone()
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(
            text=f'Отправить на почту',
            callback_data=CallReportsCallbackData(
                menu=CallReportsMenus.send_to_mail,
                **callback_data.model_dump(include={'client', 'page', 'page_date', 'call_report_id'})
            ).pack()
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text=f'Редактировать',
            callback_data=CallReportsCallbackData(
                menu=CallReportsMenus.edit_report,
                **callback_data.model_dump(include={'client', 'page', 'page_date', 'call_report_id'})
            ).pack()
        )
    )
    if client == callback_data.client:
        keyboard.row(
            types.InlineKeyboardButton(
                text=f'Назад',
                callback_data=CallReportsCallbackData(
                    menu=CallReportsMenus.my_reports,
                    **callback_data.model_dump(include={'client', 'page', 'page_date', })
                ).pack()
            )
        )
    else:
        keyboard.row(
            types.InlineKeyboardButton(
                text=f'Назад',
                callback_data=CallReportsCallbackData(
                    menu=CallReportsMenus.my_reports,
                    **callback_data.model_dump(include={'page',})
                ).pack()
            )
        )
    await callback_query.message.edit_text(
        (
            f'Протокол Встречи:\n\n'
            f'Клиент: {client}\n'
            f'Дата: {report_date.strftime(config.BASE_DATE_FORMAT)}\n'
            f'Запись встречи: {description}\n'
        ),
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(
    CallReportsCallbackData.filter(F.menu == CallReportsMenus.send_to_mail),
)
async def call_reports_send_to_mail(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
) -> None:
    user_id = callback_query.message.chat.id

    async with async_session() as session:
        user_email = await session.execute(
            select(Whitelist.user_email, ).filter(
                Whitelist.user_id == user_id,
            )
        )
        user_email = user_email.fetchone()[0]

    async with async_session() as session:
        call_report = await session.execute(
            select(CallReports.client, CallReports.report_date, CallReports.description).filter(
                CallReports.id == callback_data.call_report_id,
            )
        )
        client, report_date, description = call_report.fetchone()

    await send_to_mail(user_email, client, report_date, description)


@router.callback_query(
    CallReportsCallbackData.filter(F.menu == CallReportsMenus.edit_report),
)
async def call_reports_edit_report(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
) -> None:
    keyboard = keyboards.get_keyboard_for_view_call_report(callback_data)
    async with async_session() as session:
        call_report = await session.execute(
            select(CallReports.client, CallReports.report_date, CallReports.description).filter(
                CallReports.id == callback_data.call_report_id,
            )
        )
        client, report_date, description = call_report.fetchone()
    await callback_query.message.edit_text(
        (
            f'Протокол Встречи:\n\n'
            f'Клиент: {client}\n'
            f'Дата: {report_date.strftime(config.BASE_DATE_FORMAT)}\n'
            f'Запись встречи: {description}\n'
        ),
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(
    CallReportsCallbackData.filter(F.menu == CallReportsMenus.edit_report_name),
)
async def call_reports_edit_report_name(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
        state: FSMContext,
) -> None:
    async with async_session() as session:
        call_report = await session.execute(
            select(CallReports.client, CallReports.report_date, CallReports.description).filter(
                CallReports.id == callback_data.call_report_id,
            )
        )
        client, report_date, description = call_report.fetchone()
    await state.set_state(CallReportsEditStates.edit_clint_name)
    await state.update_data(**callback_data.model_dump())
    await callback_query.message.edit_text(
        (
            f'Изменение имени клиента.\n\n'
            f'Предыдущее значение: {callback_data.client}\n\n'
            f'Введите новое значение в чат!'
        ),
        reply_markup=None,
    )


@router.callback_query(
    CallReportsCallbackData.filter(F.menu == CallReportsMenus.edit_report_date),
)
async def call_reports_edit_report_date(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
        state: FSMContext,
) -> None:
    async with async_session() as session:
        call_report = await session.execute(
            select(CallReports.report_date).filter(
                CallReports.id == callback_data.call_report_id,
            )
        )
        report_date = call_report.fetchone()[0]

    await state.set_state(CallReportsEditStates.edit_date)
    await state.update_data(**callback_data.model_dump())
    await callback_query.message.edit_text(
        (
            f'Изменение даты.\n\n'
            f'Предыдущее значение: {report_date.strftime(config.BASE_DATE_FORMAT)}\n\n'
            f'Введите новое значение в чат'
        ),
        reply_markup=None,
    )


@router.callback_query(
    CallReportsCallbackData.filter(F.menu == CallReportsMenus.edit_report_description),
)
async def call_reports_edit_report_description(
        callback_query: types.CallbackQuery,
        callback_data: CallReportsCallbackData,
        state: FSMContext,
) -> None:
    async with async_session() as session:
        call_report = await session.execute(
            select(CallReports.description).filter(
                CallReports.id == callback_data.call_report_id,
            )
        )
        description = call_report.fetchone()[0]

    await state.set_state(CallReportsEditStates.edit_text_message)
    await state.update_data(**callback_data.model_dump())

    await callback_query.message.edit_text(
        (
            f'Изменение описания.\n\n'
            f'Предыдущее значение: {description}\n\n'
            f'Введите новое значение в чат'
        ),
        reply_markup=None,
    )


@router.message(CallReportsEditStates.edit_date)
async def call_reports_edit_date(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = keyboards.get_keyboard_for_view_call_report(await state.get_data())

    date = validate_and_parse_date(message.text)
    if date := validate_and_parse_date(message.text):
        async with async_session() as session:
            await session.execute(
                update(CallReports).values(report_date=date).where(
                    CallReports.id == data['call_report_id']
                )
            )
            await session.commit()

    async with async_session() as session:
        call_report = await session.execute(
            select(CallReports.client, CallReports.report_date, CallReports.description).filter(
                CallReports.id == data['call_report_id'],
            )
        )
        client, report_date, description = call_report.fetchone()
    await message.answer(
        (
            f'Протокол Встречи:\n\n'
            f'Клиент: {client}\n'
            f'Дата: {report_date.strftime(config.BASE_DATE_FORMAT)}\n'
            f'Запись встречи: {description}\n'
        ),
        reply_markup=keyboard.as_markup(),
    )


@router.message(CallReportsEditStates.edit_clint_name)
async def call_reports_edit_name(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = keyboards.get_keyboard_for_view_call_report(data)
    async with async_session() as session:
        await session.execute(
            update(CallReports).values(client=message.text).where(
                CallReports.id == data['call_report_id']
            )
        )
        await session.commit()

    async with async_session() as session:
        call_report = await session.execute(
            select(CallReports.client, CallReports.report_date, CallReports.description).filter(
                CallReports.id == data['call_report_id'],
            )
        )
        client, report_date, description = call_report.fetchone()
    await message.answer(
        (
            f'Протокол Встречи:\n\n'
            f'Клиент: {client}\n'
            f'Дата: {report_date.strftime(config.BASE_DATE_FORMAT)}\n'
            f'Запись встречи: {description}\n'
        ),
        reply_markup=keyboard.as_markup(),
    )


@router.message(CallReportsEditStates.edit_text_message)
async def call_reports_edit_text_message(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    keyboard = keyboards.get_keyboard_for_view_call_report(await state.get_data())

    async with async_session() as session:
        await session.execute(
            update(CallReports).values(description=message.text).where(
                CallReports.id == data['call_report_id']
            )
        )
        await session.commit()

    async with async_session() as session:
        call_report = await session.execute(
            select(CallReports.client, CallReports.report_date, CallReports.description).filter(
                CallReports.id == data['call_report_id'],
            )
        )
        client, report_date, description = call_report.fetchone()
    await message.answer(
        (
            f'Протокол Встречи:\n\n'
            f'Клиент: {client}\n'
            f'Дата: {report_date.strftime(config.BASE_DATE_FORMAT)}\n'
            f'Запись встречи: {description}\n'
        ),
        reply_markup=keyboard.as_markup(),
    )
