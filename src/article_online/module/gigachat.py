import json
from logging import Logger
from uuid import uuid4
import warnings

import requests as req

from configs.config import giga_oauth_url, giga_chat_url, giga_scope, giga_model, giga_credentials

warnings.filterwarnings('ignore')


class GigaChat:
    oauth_url = giga_oauth_url
    chat_url = giga_chat_url
    scope = giga_scope
    model = giga_model

    def __init__(self, logger: Logger):
        self._credentials = giga_credentials
        self.token = self.get_user_token()
        self.logger = logger

    def get_user_token(self) -> str:
        """Получение токена доступа к модели GigaChat"""

        headers = {
            'Authorization': f'Basic {self._credentials}',
            'RqUID': str(uuid4()),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {'scope': self.scope}
        response = req.post(self.oauth_url, headers=headers, data=data, verify=False)
        token = response.json()['access_token']
        return token

    def post_giga_query(self, text: str, prompt: str = '') -> str:
        """
        Получение ответа от модели GigaChat
        :param text: токен доступа к модели
        :param prompt: системный промпт
        return ответ модели
        """

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = json.dumps({
            'model': self.model,
            'messages': [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': text}],
            'profanity_check': False
        })

        response = req.post(url=self.chat_url, headers=headers, data=data, verify=False)
        return response.json()['choices'][0]['message']['content']

    def get_giga_answer(self, text: str, prompt: str = ''):
        """Обработчик исключений при получении ответа от GigaChat"""
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

