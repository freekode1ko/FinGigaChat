"""Описание класса RAGRouter."""
import json
import re
import urllib.parse

import requests

from configs import config, prompts
from constants.constants import DEFAULT_RAG_ANSWER, ERROR_RAG_ANSWER, GIGA_RAG_FOOTER
from constants.enums import RetrieverType
from log.bot_logger import logger, user_logger
from module.gigachat import GigaChat

giga = GigaChat(logger)


class RAGRouter:
    """Класс с классификацией запроса относительно RAG-сервисов(+GigaChat) и с получением ответа на запрос."""

    GET_METHOD = 'GET'
    POST_METHOD = 'POST'

    def __init__(self, chat_id: int, full_name: str, user_query: str, rephrase_query: str, use_rephrase: bool = True):
        """
        Инициализация экземпляра RAGRouter.

        :param chat_id:         Id Telegram чата с пользователем.
        :param full_name:       Полное имя пользователя в Telegram.
        :param user_query:      Запрос пользователя.
        :param rephrase_query:  Перефразированный запрос пользователя.
        :param use_rephrase:    Нужно ли использовать перефразированный запрос пользователя для получения ответа.
        """
        self.chat_id = chat_id
        self.full_name = full_name
        self.user_query = user_query
        self.rephrase_query = rephrase_query
        self.query = self.rephrase_query if use_rephrase else self.user_query
        self.retriever_type = self.get_rag_type()

    def get_rag_type(self) -> RetrieverType:
        """По пользовательскому запросу определяет класс рага, который нужно вызвать."""
        rag_class = RetrieverType.other  # по умолчанию
        rag_class_int = -1  # по умолчанию

        content = prompts.CLASSIFICATION_PROMPT.format(question=self.query)
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
        """Вызов ретривера относительно типа ретривера."""
        if self.retriever_type == RetrieverType.state_support:
            return self.rag_state_support()
        elif self.retriever_type == RetrieverType.qa_banker:
            return self.rag_qa_banker()
        return giga.get_giga_answer(self.query)

    def rag_qa_banker(self) -> str:
        """Формирование параметров к запросу API по новостям и получение ответа."""
        query = urllib.parse.quote(self.query)
        query_part = f'queries?query={query}'
        req_kwargs = dict(
            url=config.BASE_QABANKER_URL.format(query_part),
            timeout=config.POST_TO_SERVICE_TIMEOUT
        )
        return self._request_to_api(**req_kwargs)

    def rag_state_support(self) -> str:
        """Формирование параметров к запросу API по господдержке и получение ответа."""
        req_kwargs = dict(
            url=config.QUERY_STATE_SUPPORT_URL,
            json={'body': self.user_query},
            timeout=config.POST_TO_SERVICE_TIMEOUT
        )

        return self._request_to_api(self.POST_METHOD, **req_kwargs)

    def _request_to_api(self, request_method: str = GET_METHOD, **kwargs) -> str:
        """
        Отправляет запрос к RAG API И формирует ответ.

        :param  request_method:     HTTP метод.
        :param kwargs:              Параметры http запроса.
        return:                     Отформатированный ответ.
        """
        try:
            rag_response = requests.request(method=request_method, **kwargs)
            rag_response.raise_for_status()
            rag_answer = rag_response.text if request_method == self.GET_METHOD else rag_response.json()['body']

            response = f'{rag_answer}\n\n{GIGA_RAG_FOOTER}' if rag_answer != DEFAULT_RAG_ANSWER else rag_answer
            user_logger.info('*%d* %s - "%s" : На запрос ВОС ответила: "%s"' %
                             (self.chat_id, self.full_name, self.query, rag_answer))

        except requests.RequestException as e:
            logger.critical('ERROR : ВОС не сформировал ответ по причине: %s' % e)
            user_logger.critical('*%d* %s - "%s" : ВОС не сформировал ответ по причине: "%s"' %
                                 (self.chat_id, self.full_name, self.query, e))
            response = ERROR_RAG_ANSWER

        return response
