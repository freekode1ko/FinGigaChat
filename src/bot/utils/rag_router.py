from enum import Enum
import json
import re
import urllib.parse

import requests

from configs import config
from constants.constants import giga_rag_footer
from log.bot_logger import logger, user_logger
from module.gigachat import GigaChat

giga = GigaChat(logger)


class RetrieverType(Enum):
    """Типы ретриверов"""
    other = 0  # простое обращение к гигачат
    state_support = 1  # ретривер по господдержке
    qa_banker = 2  # ретривер по новостям и финансовым показателям


class RAGRouter:

    def __init__(self, chat_id: int, full_name: str, query: str):
        self.chat_id = chat_id
        self.full_name = full_name
        self.query = query
        self.retriever_type = self.get_rag_type()

    def get_rag_type(self):
        """По пользовательскому запросу определяет класс рага, который нужно вызвать"""

        rag_class = RetrieverType.other  # по умолчанию
        rag_class_int = -1  # по умолчанию

        content = config.classification_prompt.format(question=self.query)
        response = giga.get_giga_answer(content)

        try:
            response_json = json.loads(response)
            rag_class_int = int(response_json['answer'])
        except json.decoder.JSONDecodeError:
            pattern = r'answer\W*\s(\d)'
            matches = re.search(pattern, response)
            if matches:
                rag_class_int = int(matches.group(1))

        if rag_class_int == RetrieverType.state_support.value:
            rag_class = RetrieverType.state_support
        elif rag_class_int == RetrieverType.qa_banker.value:
            rag_class = RetrieverType.qa_banker

        return rag_class

    def get_response_from_rag(self) -> str:
        """Вызов ретривера относительно типа ретривера"""
        if self.retriever_type == RetrieverType.state_support:
            return self.rag_state_support()

        elif self.retriever_type == RetrieverType.qa_banker:
            return self.rag_qa_banker()

        else:
            return giga.get_giga_answer(self.query)

    def rag_qa_banker(self) -> str:
        """Получение ответа от ретривера по новостям"""
        try:
            query = urllib.parse.quote(self.query)
            query_part = f'queries?query={query}'
            rag_response = requests.get(
                url=config.BASE_QABANKER_URL.format(query_part),
                timeout=config.POST_TO_SERVICE_TIMEOUT)
            if rag_response.status_code == 200:
                rag_answer = rag_response.text
                response = f'{rag_answer}\n\n{giga_rag_footer}'
                user_logger.info(f'*{self.chat_id}* {self.full_name} - "{self.query}" : На запрос ВОС ответила: "{rag_answer}"')
            else:
                response = 'Извините, я пока не могу ответить на ваш запрос'
        except Exception as e:
            logger.critical(f'ERROR : ВОС не сформировал ответ по причине: {e}"')
            user_logger.critical(f'*{self.chat_id}* {self.full_name} - "{self.query}" : ВОС не сформировал ответ по причине: {e}"')
            response = 'Извините, я пока не могу ответить на ваш запрос'

        return response

    def rag_state_support(self) -> str:
        """Получение ответа от ретривера по господдержке"""
        return 'использовался раг по господдержке'
