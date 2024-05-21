"""Описание класса GigaChat."""
import json
from logging import Logger
from typing import ClassVar
from uuid import uuid4
import warnings

import requests as req

from configs.config import giga_chat_url, giga_credentials, giga_model, giga_oauth_url, giga_scope

warnings.filterwarnings('ignore')


class GigaChat:
    """
    Класс для взаимодействия с моделью GigaChat через OAuth авторизацию и отправку запросов.

    Атрибуты:
    OAUTH_URL:      URL для OAuth авторизации.
    CHAT_URL:       URL для отправки запросов к модели GigaChat.
    SCOPE:          Область действия для получения токена.
    MODEL:          Название модели GigaChat.
    CREDENTIALS:    Название модели GigaChat.
    """

    OAUTH_URL: ClassVar[str] = giga_oauth_url
    CHAT_URL: ClassVar[str] = giga_chat_url
    SCOPE: ClassVar[str] = giga_scope
    MODEL: ClassVar[str] = giga_model
    CREDENTIALS: ClassVar[str] = giga_credentials

    def __init__(self, logger: Logger):
        """
        Инициализация экземпляра GigaChat.

        :param logger: Логгер для записи событий и ошибок.
        """
        self.token = self.get_user_token()
        self.logger = logger

    @staticmethod
    def get_user_token() -> str:
        """Получение токена доступа к модели GigaChat."""
        headers = {
            'Authorization': f'Basic {GigaChat.CREDENTIALS}',
            'RqUID': str(uuid4()),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'scope': GigaChat.SCOPE}
        response = req.post(GigaChat.OAUTH_URL, headers=headers, data=data, verify=False)
        token = response.json()['access_token']
        return token

    def post_giga_query(self, text: str, prompt: str = '') -> str:
        """
        Получение ответа от модели GigaChat.

        :param text:     Токен доступа к модели.
        :param prompt:   Системный промпт.
        :return:         Ответ модели.
        """
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = json.dumps({
            'model': GigaChat.MODEL,
            'messages': [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': text}],
            'profanity_check': False,
            # 'temperature': 0.01
        })

        response = req.post(url=GigaChat.CHAT_URL, headers=headers, data=data, verify=False)
        return response.json()['choices'][0]['message']['content']

    def get_giga_answer(self, text: str, prompt: str = '') -> str:
        """
        Обработчик исключений при получении ответа от GigaChat.

        :param text:    Запрос пользователя (user prompt).
        :param prompt:  Текста промпта.
        :return:        Ответ от GigaChat.
        """
        try:
            giga_answer = self.post_giga_query(text=text, prompt=prompt)
        except AttributeError:
            self.logger.debug('Перевыпуск токена для общения с GigaChat')
            self.token = self.get_user_token()
            giga_answer = self.post_giga_query(text=text)
        except KeyError:
            self.logger.debug('Перевыпуск токена для общения с GigaChat')
            self.token = self.get_user_token()
            giga_answer = self.post_giga_query(text=text)
            self.logger.critical(f'msg - {text}, prompt - {prompt}'
                                 f'KeyError (некорректная выдача ответа GigaChat), '
                                 f'ответ после переформирования запроса')
        return giga_answer
