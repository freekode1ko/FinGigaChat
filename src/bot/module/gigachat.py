"""Описание класса GigaChat."""
import json
import warnings
from logging import Logger
from typing import ClassVar
from uuid import uuid4

import requests as req

from configs.config import giga_chat_url, giga_credentials, giga_model, giga_oauth_url, giga_scope
from utils.sessions import GigaChatClient, GigaOauthClient

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

    OAUTH_URL_PART: ClassVar[str] = '/api/v2/oauth'
    CHAT_URL_PART: ClassVar[str] = '/api/v1/chat/completions'
    SCOPE: ClassVar[str] = giga_scope
    MODEL: ClassVar[str] = giga_model
    CREDENTIALS: ClassVar[str] = giga_credentials
    TEMPERATURE: ClassVar[float] = 0.5
    MAX_TOKENS: ClassVar[int] = 0.5

    def __init__(self, logger: Logger) -> None:
        """
        Инициализация экземпляра GigaChat.

        :param logger: Логгер для записи событий и ошибок.
        """
        self.token = self.get_user_token()
        self.logger = logger

    @staticmethod
    def _get_headers_and_data_for_token() -> tuple[dict[str, str], dict[str, str]]:
        """
        Формирование хэдера и даты для формирования токена.

        :return: Header и data для получения токена к GigaChat.
        """
        headers = {
            'Authorization': f'Basic {GigaChat.CREDENTIALS}',
            'RqUID': str(uuid4()),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'scope': GigaChat.SCOPE}
        return headers, data

    @staticmethod
    def _get_headers_and_data_for_chat(
            token: str,
            text: str,
            prompt: str,
            temperature: float
    ) -> tuple[dict[str, str], str]:
        """
        Формирование хэдера и даты для запроса к модели.

        :param token:           Токен доступа к модели.
        :param text:            Пользовательское сообщение.
        :param prompt:          Системный промпт.
        :param temperature:     Параметр температуры для модели.
        :return:                Header и data для отправки запроса к GigaChat.
        """
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = json.dumps({
            'model': GigaChat.MODEL,
            'messages': [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': text}],
            'profanity_check': False,
            'temperature': temperature,
            'max_tokens ': GigaChat.MAX_TOKENS
        })
        return headers, data

    @staticmethod
    def get_user_token() -> str:
        """Получение токена доступа к модели GigaChat."""
        headers, data = GigaChat._get_headers_and_data_for_token()
        url = giga_oauth_url + GigaChat.OAUTH_URL_PART
        response = req.post(url, headers=headers, data=data, verify=False)
        token = response.json()['access_token']
        return token

    def post_giga_query(self, text: str, prompt: str, temperature: float) -> str:
        """
        Получение ответа от модели GigaChat.

        :param text:          Пользовательское сообщение.
        :param prompt:        Системный промпт.
        :param temperature:   Параметр температуры для модели.
        :return:              Ответ модели.
        """
        headers, data = self._get_headers_and_data_for_chat(self.token, text, prompt, temperature)
        url = giga_chat_url + GigaChat.CHAT_URL_PART
        response = req.post(url, headers=headers, data=data, verify=False)
        return response.json()['choices'][0]['message']['content']

    def get_giga_answer(self, text: str, prompt: str = '', temperature: float = TEMPERATURE) -> str:
        """
        Обработчик исключений при получении ответа от GigaChat.

        :param text:          Запрос пользователя (user prompt).
        :param prompt:        Текста промпта.
        :param temperature:   Параметр температуры для модели.
        :return:              Ответ от GigaChat.
        """
        try:
            giga_answer = self.post_giga_query(text=text, prompt=prompt, temperature=temperature)
        except AttributeError:
            self.token = self.get_user_token()
            giga_answer = self.post_giga_query(text=text, prompt=prompt, temperature=temperature)
        except KeyError as key_error:
            self.token = self.get_user_token()
            giga_answer = self.post_giga_query(text=text, prompt=prompt, temperature=temperature)
            self.logger.critical(f'msg - {text}, prompt - {prompt} : KeyError ({key_error.args})')
        return giga_answer

    @staticmethod
    async def aget_user_token() -> str:
        """Асинхронное получение токена доступа к модели GigaChat."""
        headers, data = GigaChat._get_headers_and_data_for_token()
        giga_oauth_session = GigaOauthClient().session
        async with giga_oauth_session.post(GigaChat.OAUTH_URL_PART, headers=headers, data=data) as response:
            response = await response.json()
            token = response['access_token']
            return token

    async def apost_giga_query(self, text: str, prompt: str, temperature: float) -> str:
        """
        Асинхронное получение ответа от модели GigaChat.

        :param text:          Токен доступа к модели.
        :param prompt:        Системный промпт.
        :param temperature:   Параметр температуры для модели.
        :return:              Ответ модели.
        """
        headers, data = GigaChat._get_headers_and_data_for_chat(self.token, text, prompt, temperature)
        giga_chat_session = GigaChatClient().session
        async with giga_chat_session.post(GigaChat.CHAT_URL_PART, headers=headers, data=data) as response:
            response = await response.json()
            return response['choices'][0]['message']['content']

    async def aget_giga_answer(self, text: str, prompt: str = '', temperature: float = TEMPERATURE) -> str:
        """
        Асинхронный обработчик исключений при получении ответа от GigaChat.

        :param text:          Запрос пользователя (user prompt).
        :param prompt:        Текста промпта.
        :param temperature:   Параметр температуры для модели.
        :return:              Ответ от GigaChat.
        """
        try:
            giga_answer = await self.apost_giga_query(text=text, prompt=prompt, temperature=temperature)
        except AttributeError:
            self.token = await self.aget_user_token()
            giga_answer = await self.apost_giga_query(text=text, prompt=prompt, temperature=temperature)
        except KeyError as key_error:
            giga_oauth = GigaOauthClient()
            giga_chat = GigaChatClient()
            await giga_oauth.recreate()
            await giga_chat.recreate()

            self.token = await self.aget_user_token()
            giga_answer = await self.apost_giga_query(text=text, prompt=prompt, temperature=temperature)
            self.logger.critical(f'msg - {text}, prompt - {prompt} : KeyError ({key_error.args})')
        return giga_answer
