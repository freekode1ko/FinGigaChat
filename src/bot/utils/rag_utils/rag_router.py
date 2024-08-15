"""Описание класса RAGRouter."""
import json
import re
import urllib.parse

from aiohttp import ClientError, ClientSession

from configs import config, prompts
from constants.texts import texts_manager
from constants.enums import HTTPMethod, RetrieverType
from log.bot_logger import logger, user_logger
from module.gigachat import GigaChat
from utils.sessions import RagQaBankerClient, RagStateSupportClient

giga = GigaChat(logger)


class RAGRouter:
    """Класс с классификацией запроса относительно RAG-сервисов(+GigaChat) и с получением ответа на запрос."""

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
        self.retriever_type = None

    async def get_rag_type(self) -> None:
        """По пользовательскому запросу определяет класс рага, который нужно вызвать."""
        rag_class = RetrieverType.other  # по умолчанию
        rag_class_int = -1  # по умолчанию

        content = prompts.CLASSIFICATION_PROMPT.format(question=self.query)
        response = await giga.aget_giga_answer(content)

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

        self.retriever_type = rag_class

    @staticmethod
    def add_question_mark(query: str) -> str:
        """
        Добавляет вопросительный знак в конец запроса, если его нет.

        :param query: Запрос.
        :return:      Запрос с вопросительным знаком в конце.
        """
        query = query.strip()
        return query if query[-1] == '?' else query + '?'

    async def get_response(self) -> str:
        """Вызов ретривера относительно типа ретривера."""
        if self.retriever_type == RetrieverType.state_support:
            return await self.rag_state_support()
        elif self.retriever_type == RetrieverType.qa_banker:
            return await self.rag_qa_banker()
        return await self._request_to_giga()

    async def rag_qa_banker(self) -> str:
        """Формирование параметров к запросу API по новостям и получение ответа."""
        query = self.add_question_mark(self.query)
        query = urllib.parse.quote(query)
        query_part = f'/api/queries?query={query}'
        req_kwargs = dict(
            url=query_part,
            timeout=config.POST_TO_SERVICE_TIMEOUT
        )
        session = RagQaBankerClient().session
        return await self._request_to_rag_api(session, **req_kwargs)

    async def rag_state_support(self) -> str:
        """Формирование параметров к запросу API по господдержке и получение ответа."""
        req_kwargs = dict(
            url='/api/v1/question',
            json={'body': self.query},
            timeout=config.POST_TO_SERVICE_TIMEOUT
        )
        session = RagStateSupportClient().session
        return await self._request_to_rag_api(session, HTTPMethod.POST, **req_kwargs)

    async def _request_to_rag_api(self,
                                  session: ClientSession,
                                  request_method: str = HTTPMethod,
                                  **kwargs) -> str:
        """
        Отправляет запрос к RAG API И формирует ответ.

        :param  session:            Сессия для подключения.
        :param  request_method:     HTTP метод.
        :param kwargs:              Параметры http запроса.
        :return:                    Оригинальный ответ RAG.
        """
        try:
            async with session.request(method=request_method, **kwargs) as rag_response:
                if request_method == HTTPMethod.GET:
                    rag_answer = await rag_response.text()
                else:
                    rag_answer = await rag_response.json()
                    rag_answer = rag_answer['body']

            user_logger.info('*%d* %s - "%s" : На запрос ВОС ответила: "%s"' %
                             (self.chat_id, self.full_name, self.query, rag_answer))
        except ClientError as e:
            logger.critical('ERROR : ВОС не сформировал ответ по причине: %s' % e)
            user_logger.critical('*%d* %s - "%s" : ВОС не сформировал ответ по причине: "%s"' %
                                 (self.chat_id, self.full_name, self.query, e))
        else:
            return rag_answer
        return texts_manager.RAG_ERROR_ANSWER

    async def _request_to_giga(self) -> str:
        """
        Получение и форматирование ответа от GigaChat.

        :return:   Оригинальный ответ GigaChat и отформатированный ответ.
        """
        try:
            giga_answer = await giga.aget_giga_answer(text=self.query)
            user_logger.info(f'*{self.chat_id}* {self.full_name} - "{self.query}" : '
                             f'На запрос GigaChat ответил: "{giga_answer}"')
        except Exception as e:
            giga_answer = texts_manager.RAG_ERROR_ANSWER
            logger.critical(f'ERROR : GigaChat не сформировал ответ по причине: {e}"')
            user_logger.critical(f'*{self.chat_id}* {self.full_name} - "{self.query}" : '
                                 f'GigaChat не сформировал ответ по причине: {e}"')
        return giga_answer
