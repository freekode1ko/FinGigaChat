import json
import requests as req
from config import chat_base_url, user_cred


class GigaChat:
    chat_base_url = chat_base_url

    def get_user_token(self) -> str:
        """
        Get user token
        :return: User token as string.
        """
        headers = {'content-type': 'application/json'}
        ans = req.post('{}token'.format(self.chat_base_url), timeout=30, headers=headers,
                       auth=(user_cred[0], user_cred[1]), verify=False)
        token = ans.json()['tok']

        return token

    def ask_giga_chat(self, question: str, token: str) -> req.models.Response:
        """
        Send text to GigaChat
        :param question: Text to ask GigaChat
        :param token: User token
        :return: GigaChat answer as object requests.models.Response
        """
        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": "{}".format(question)
                }
            ],
            "model": "GigaChat:latest",
            "profanity_check": False,
            "repetition_penalty": 1,
            "temperature": 0.1
        })
        headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

        return req.request("POST", '{}chat/completions'.format(self.chat_base_url),
                           headers=headers, data=payload, verify=False)
