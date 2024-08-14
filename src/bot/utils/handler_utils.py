"""Общий доп функционал для обработчиков тг бота"""
import os
import subprocess

import requests
import speech_recognition as sr
from aiogram import types
from aiogram.enums import ChatAction
from aiogram.types import Message

from configs import config
from constants import enums
from db.api.client import client_db
from log.bot_logger import logger, user_logger
from module.article_process import ArticleProcess
from utils.base import process_fin_table


async def get_client_financial_indicators(
        callback_query: types.CallbackQuery,
        client_id: int,
        fin_indicator_type: enums.FinancialIndicatorsType,
) -> None:
    """
    Отправка пользователю фин показателей по клиенту

    :param callback_query:      Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param client_id:           Выбранный клиент
    :param fin_indicator_type:  Выбранный тип фин показателей
    """
    chat_id = callback_query.message.chat.id
    user_msg = f'get_client_financial_indicators:{client_id}:{fin_indicator_type.value}'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client = await client_db.get(client_id)

    ap_obj = ArticleProcess(logger)
    client_fin_tables = await ap_obj.get_client_fin_indicators(client_id)
    if not client_fin_tables.empty:
        await callback_query.bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)

        # Создание и отправка таблицы
        await process_fin_table(
            callback_query,
            client['name'],
            fin_indicator_type.table_name,
            client_fin_tables[fin_indicator_type.name][0],
            logger,
        )
    else:
        msg_text = f'По клиенту {client["name"]} отсутствуют финансовые показатели'
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - "{user_msg}"')


async def audio_to_text(message: Message) -> str:
    """
    Превращает аудио сообщение в текст

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :return: строку полученную из аудио сообщения
    """
    result = ''
    path_to_file_oga = ''
    path_to_file_wav = ''

    try:
        logger.info(f'Audio Recognition: Start audio_to_text for user id: {message.chat.id}')
        file_id = message.voice.file_id
        audio_file = await message.bot.get_file(file_id)

        audio_file_url = f'https://api.telegram.org/file/bot{config.api_token}/{audio_file.file_path}'
        req = requests.get(audio_file_url)
        path_to_file_oga = config.TMP_VOICE_FILE_DIR / f'{file_id}.oga'

        with open(path_to_file_oga, 'wb') as f:
            f.write(req.content)

        path_to_file_wav = config.TMP_VOICE_FILE_DIR / f'{file_id}.wav'

        process = subprocess.run(['ffmpeg', '-i', str(path_to_file_oga), str(path_to_file_wav)])  # noqa:D200, F841

        r = sr.Recognizer()
        voice_message = sr.AudioFile(str(path_to_file_wav))
        with voice_message as source:
            audio = r.record(source)

        try:
            result = r.recognize_google(audio, language='ru_RU')
            logger.info(f'Audio Recognition: Успешная обработка аудио через гугл для {message.chat.id}')
        except Exception as e:
            logger.error(f'Audio Recognition: Не успешная обработка аудио через гугл для {message.chat.id} из-за {e}')
            result = r.recognize_whisper(audio, model=config.WHISPER_MODEL, language='ru')
            logger.info(f'Audio Recognition: Успешная обработка аудио через whisper для {message.chat.id}')
    except Exception as e:
        logger.error(f'Audio Recognition: Не успешная обработка аудио для {message.chat.id} из-за {e}')
    finally:
        if path_to_file_wav and os.path.exists(path_to_file_wav):
            os.remove(path_to_file_wav)
        if path_to_file_oga and os.path.exists(path_to_file_oga):
            os.remove(path_to_file_oga)
        logger.info(f'Audio Recognition: Успешная обработка аудио для {message.chat.id}')
        return result
