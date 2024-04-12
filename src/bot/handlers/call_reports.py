import os
import subprocess

from sqlalchemy import text

from module.mail_parse import SmtpSend
import requests
import speech_recognition as sr
from configs.config import api_token, TMP_VOICE_FILE_DIR, WHISPER_MODEL, mail_username, mail_password, mail_smpt_server, mail_smpt_port
from datetime import datetime
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from db.database import engine

from utils.base import user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())


class CallReportsStates(StatesGroup):
    enter_clint_name = State()
    enter_date = State()
    enter_text_message = State()
    final_check = State()


def is_validate_and_parse_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%d.%m.%Y")
        return date_obj.date()
    except ValueError:
        return


@router.message(Command('call_reports'))
async def call_reports(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    if await user_in_whitelist(message.from_user.model_dump_json()):
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            types.InlineKeyboardButton(text='Создать новый протокол встречи', callback_data='call_reports:create_new'))
        keyboard.row(
            types.InlineKeyboardButton(text='Посмотреть мои протоколы', callback_data='call_reports:my_reports'))

        await message.answer(
            'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?',
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(F.data.startswith('call_reports'))
async def call_reports_handler(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    match callback_query.data.split(':')[1]:
        case 'create_new':
            await callback_query.message.answer(
                'Вы перешли в режим записи протокола встречи с клиентом следуйте инструкциям, чтобы завершить процесс.',
            )
            await callback_query.message.answer(
                'Важно: Пожалуйста, не включайте в отчет информацию, превышающую уровень конфиденциальности K4. Ваша ответственность — обеспечить соблюдение норм конфиденциальности.',
            )
            await callback_query.message.answer(
                'Введите, пожалуйста, наименование клиента с кем проходила встреча:',
            )

            await state.clear()
            await state.set_state(CallReportsStates.enter_clint_name)
        case 'my_reports':
            await callback_query.message.answer(
                'Данный функционал будет позже',
            )
        case 'send_to_mail':
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


            SS = SmtpSend()  # TODO: Вынести в with открытие, отправку и закрытия
            SS.get_connection(mail_username, mail_password, mail_smpt_server, mail_smpt_port)
            SS.send_msg(
                mail_username,
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
            with engine.connect() as conn:

                query = text(
                    f'INSERT INTO bot_call_reports (user_id, client, report_date, description) '
                    f'VALUES (:user_id, :client, :date, :report) '
                )

                data = conn.execute(query)
                conn.commit()
        case _:
            pass


@router.message(CallReportsStates.enter_clint_name)
async def enter_clint_name(message: types.Message, state: FSMContext) -> None:
    if True:  # FIXME
        await message.answer(
            'Укажите дату встречи в формате ДД.ММ.ГГГГ:',
        )
        await state.set_state(CallReportsStates.enter_date)
        await state.update_data(
            client=message.text,
        )


@router.message(CallReportsStates.enter_date)
async def enter_date(message: types.Message, state: FSMContext) -> None:
    if date := is_validate_and_parse_date(message.text):
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

async def audio_to_text(message: types.Message,) -> str:
    try:
        file_id = message.voice.file_id
        audio_file = await message.bot.get_file(file_id)

        audio_file_url = f"https://api.telegram.org/file/bot{api_token}/{audio_file.file_path}"
        req = requests.get(audio_file_url)
        path_to_file_oga = TMP_VOICE_FILE_DIR / f'{file_id}.oga'

        with open(path_to_file_oga, 'wb') as f:
            f.write(req.content)

        path_to_file_wav = TMP_VOICE_FILE_DIR / f'{file_id}.wav'

        process = subprocess.run(['ffmpeg', '-i', str(path_to_file_oga), str(path_to_file_wav)])

        r = sr.Recognizer()
        voice_message = sr.AudioFile(str(path_to_file_wav))
        with voice_message as source:
            audio = r.record(source)
        try:
            result = r.recognize_google(audio, language="ru_RU")
        except Exception:
            result = r.recognize_whisper(audio, model=WHISPER_MODEL, language="ru")
    except Exception as e:
        pass
    finally:
        os.remove(path_to_file_wav)
        os.remove(path_to_file_oga)
        return result


@router.message(CallReportsStates.enter_text_message, F.content_type.in_({'voice', 'text',}), )
async def enter_text_message(message: types.Message, state: FSMContext) -> None:
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