"""Вспомогательные функции при создании call report'ов"""
import os
import subprocess
from datetime import datetime
from typing import Optional

import requests
import speech_recognition as sr
from aiogram.types import Message

from configs import config
from log.bot_logger import logger


def validate_and_parse_date(date_str: str) -> Optional[datetime.date]:
    """
    Валидация строки с датой и возвращение ее в datetime object

    :param date_str: date str
    :return: Возвращает время в питоновском формате
    """
    try:
        date_obj = datetime.strptime(date_str, config.BASE_DATE_FORMAT)
        return date_obj.date()
    except ValueError:
        return


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
        logger.info(f'Call Report: Start audio_to_text for user id: {message.chat.id}')
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
            logger.info(f'Call Report: Успешная обработка аудио через гугл для {message.chat.id}')
        except Exception as e:
            logger.error(f'Call Report: Не успешная обработка аудио через гугл для {message.chat.id} из-за {e}')
            result = r.recognize_whisper(audio, model=config.WHISPER_MODEL, language='ru')
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
