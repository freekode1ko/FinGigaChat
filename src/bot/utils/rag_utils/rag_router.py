"""Описание класса RAGRouter."""
import asyncio
import json
import re
from copy import deepcopy
from typing import Any

from aiohttp import ClientError, ClientSession

from configs import config, prompts
from constants.constants import DEFAULT_RAG_ANSWER
from constants.enums import HTTPMethod, RetrieverType
from constants.texts import texts_manager
from log.bot_logger import logger, user_logger
from module.gigachat import GigaChat
from utils.sessions import RagQaBankerClient, RagQaResearchClient, RagStateSupportClient

giga = GigaChat(logger)


class RAGRouter:
    """Класс с классификацией запроса относительно RAG-сервисов(+GigaChat) и с получением ответа на запрос."""

    RAG_BAD_ANSWERS = (DEFAULT_RAG_ANSWER, texts_manager.RAG_ERROR_ANSWER)

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
        self.req_kwargs = dict(
            url='/api/v1/question',
            json={'body': self.add_question_mark(self.query)},
            timeout=config.POST_TO_SERVICE_TIMEOUT
        )

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

    async def get_response(self) -> str | dict[str, Any]:
        """Вызов ретривера относительно типа ретривера."""
        if self.retriever_type == RetrieverType.state_support:
            return await self.rag_state_support()
        elif self.retriever_type == RetrieverType.qa_banker:
            return await self.get_combination_response()
        return await self._request_to_giga()

    async def rag_qa_banker(self) -> dict[str, Any]:
        """Формирование параметров к запросу API по новостям и получение ответа."""
        session = RagQaBankerClient().session
        return await self._request_to_rag_api(session, **self.req_kwargs)

    async def rag_state_support(self) -> dict[str, Any]:
        """Создание сессии для API по господдержке и получение ответа."""
        session = RagStateSupportClient().session
        return await self._request_to_rag_api(session, **self.req_kwargs)

    async def rag_qa_research(self) -> dict[str, Any]:
        """Создание сессии для API по ВОС CIB Research и получение ответа."""
        session = RagQaResearchClient().session
        req_kwargs = deepcopy(self.req_kwargs)
        data = req_kwargs['json']
        data['with_metadata'] = True
        req_kwargs['json'] = data
        return await self._request_to_rag_api(session, **req_kwargs)

    async def _request_to_rag_api(self, session: ClientSession, **kwargs) -> dict[str, Any]:
        """
        Отправляет запрос к RAG API И формирует ответ.

        :param  session:            Сессия для подключения.
        :param  kwargs:             Параметры http запроса.
        :return:                    Словарь ответа от RAG.
        """
        try:
            async with session.request(method=HTTPMethod.POST, **kwargs) as rag_response:
                rag_response_dict = await rag_response.json()
            user_logger.info('*%d* %s - "%s" : На запрос ВОС ответила: "%s"' %
                             (self.chat_id, self.full_name, self.query, rag_response_dict))
        except ClientError as e:
            logger.critical('ERROR : ВОС не сформировал ответ по причине: %s' % e)
            user_logger.critical('*%d* %s - "%s" : ВОС не сформировал ответ по причине: "%s"' %
                                 (self.chat_id, self.full_name, self.query, e))
        else:
            return rag_response_dict
        return {'body': texts_manager.RAG_ERROR_ANSWER}

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

    async def get_combination_response(self) -> dict[str, Any]:
        """Комбинация ответов от разных рагов."""
        banker_json, research_json = await asyncio.gather(self.rag_qa_banker(), self.rag_qa_research())
        banker, research = banker_json['body'], research_json['body']
        response = self.format_combination_answer(banker, research)
        metadata = research_json.get('metadata')
        return {'body': response, 'metadata': metadata}

    def format_combination_answer(self, banker: str, research: str) -> str:
        if banker == research == texts_manager.RAG_ERROR_ANSWER:
            return texts_manager.RAG_ERROR_ANSWER

        response = ''
        if banker not in self.RAG_BAD_ANSWERS:
            response += banker
        if research not in self.RAG_BAD_ANSWERS:
            response += texts_manager.RAG_RESEARCH_SUFFIX.format(answer=research)
        return response.strip() or DEFAULT_RAG_ANSWER
