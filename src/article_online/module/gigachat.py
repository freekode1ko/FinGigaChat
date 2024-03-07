from uuid import uuid4
import json

import requests as req

from configs.config import giga_oauth_url, giga_chat_url, giga_scope, giga_model, giga_credentials


class GigaChat:
    oauth_url = giga_oauth_url
    chat_url = giga_chat_url
    scope = giga_scope
    model = giga_model

    def __init__(self):
        self._credentials = giga_credentials

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

    def ask_giga_chat(self, token: str, text: str, prompt: str = '') -> req.models.Response:
        """
        Получение ответа от модели GigaChat
        :param token: токен доступа к модели
        :param text: токен доступа к модели
        :param prompt: системный промпт
        return response с результатом ответа модели
        """

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = json.dumps({
            'model': self.model,
            'messages': [{'role': 'system', 'content': prompt}, {'role': 'user', 'content': text}],
            'profanity_check': False
        })

        response = req.post(url=self.chat_url, headers=headers, data=data, verify=False)
        # answer = req.json()['choices'][0]['message']['content']
        return response
