import openai

from config import api_key_gpt

# TODO: установить openai==0.28.1
# TODO: создать токен


class ChatGPT:
    def __init__(self):
        openai.api_key = api_key_gpt

    def ask_chat_gpt(self, text: str, prompt: str = ''):
        """
        Make summarization or make answer by ChatGPT
        :param prompt: system prompt to ChatGPT
        :param text: text
        :return: ChatGPT answer as object requests.models.Response
        """
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo', messages=[{'role': 'system', 'content': prompt}, {'role': 'user', 'content': text}]
        )

        return completion
