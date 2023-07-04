import json
import requests as req
from config import chat_base_url
from config import user_cred
giga_version = ''


class GigaChat:
    chat_base_url = chat_base_url

    def __get_giga_version(self, token: str) -> None:
        """
        get version of GigaChat model
        :param token: User token
        :return: None
        """
        global giga_version
        headers = {'accept': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
        gig_version_ans = req.get('{}models'.format(self.chat_base_url), timeout=30,
                                  headers=headers, verify=False)
        try:
            giga_version = gig_version_ans.json()['data'][0]['id']
            print('GigaChat version is: {}'.format(giga_version))
        except KeyError:
            print('Error while getting gigachat version: HTTP code - {},\n{}'.format(giga_version, giga_version.text))

    def get_user_token(self) -> str:
        """
        Get user token
        :return: User token as string.
        """
        headers = {'content-type': 'application/json'}
        ans = req.post('{}token'.format(self.chat_base_url), timeout=30, headers=headers,
                       auth=(user_cred[0], user_cred[1]), verify=False)
        token = ans.json()['tok']
        self.__get_giga_version(token)
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
            "model": "{}".format(giga_version),
            "profanity_check": False,
            "temperature": 0.1
        })
        headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

        return req.request("POST", '{}chat/completions'.format(self.chat_base_url),
                           headers=headers, data=payload, verify=False)
