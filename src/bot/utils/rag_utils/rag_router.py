"""Описание класса RAGRouter."""
import asyncio
import json
import re
from copy import deepcopy
from typing import Any

from aiohttp import ClientError, ClientSession

from configs import config, prompts
from constants import enums
from constants.constants import DEFAULT_RAG_ANSWER
from constants.enums import HTTPMethod, RetrieverType
from constants.texts import texts_manager
from db.api.research import research_db
from db.database import async_session
from log.bot_logger import logger, user_logger
from module.gigachat import GigaChat

from utils.base import is_has_access_to_feature
from utils.rag_utils.rag_format import extract_summarization
from utils.sessions import RagQaBankerClient, RagQaResearchClient, RagStateSupportClient, RagWebClient

giga = GigaChat(logger)


class RAGRouter:
    """Класс с классификацией запроса относительно RAG-сервисов(+GigaChat) и с получением ответа на запрос."""

    RAG_BAD_ANSWERS = (DEFAULT_RAG_ANSWER, texts_manager.RAG_ERROR_ANSWER)

    def __init__(self, user_id: int, full_name: str, user_query: str, rephrase_query: str, use_rephrase: bool = True):
        """
        Инициализация экземпляра RAGRouter.

        :param user_id:         Id Telegram пользователя.
        :param full_name:       Полное имя пользователя в Telegram.
        :param user_query:      Запрос пользователя.
        :param rephrase_query:  Перефразированный запрос пользователя.
        :param use_rephrase:    Нужно ли использовать перефразированный запрос пользователя для получения ответа.
        """
        self.user_id = user_id
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
        async with async_session() as ses:
            if not await is_has_access_to_feature(ses, self.user_id, enums.FeatureType.rag_research):
                return {'body': DEFAULT_RAG_ANSWER}
        session = RagQaResearchClient().session
        req_kwargs = deepcopy(self.req_kwargs)
        req_kwargs['json']['with_metadata'] = True
        return await self._request_to_rag_api(session, **req_kwargs)

    async def rag_web(self) -> dict[str, Any]:
        """Создание сессии для API по ВОС web_retriever и получение ответа"""
        session = RagWebClient().session
        return await self._request_to_rag_api(session, **self.req_kwargs)

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
                             (self.user_id, self.full_name, self.query, rag_response_dict))
        except ClientError as e:
            logger.critical('ERROR : ВОС не сформировал ответ по причине: %s' % e)
            user_logger.critical('*%d* %s - "%s" : ВОС не сформировал ответ по причине: "%s"' %
                                 (self.user_id, self.full_name, self.query, e))
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
            user_logger.info(f'*{self.user_id}* {self.full_name} - "{self.query}" : '
                             f'На запрос GigaChat ответил: "{giga_answer}"')
        except Exception as e:
            giga_answer = texts_manager.RAG_ERROR_ANSWER
            logger.critical(f'ERROR : GigaChat не сформировал ответ по причине: {e}"')
            user_logger.critical(f'*{self.user_id}* {self.full_name} - "{self.query}" : '
                                 f'GigaChat не сформировал ответ по причине: {e}"')
        return giga_answer

    async def get_combination_response(self) -> dict[str, Any]:
        """Комбинация ответов от разных рагов."""
        banker_json, research_json, web_json = await asyncio.gather(self.rag_qa_banker(), self.rag_qa_research(), self.rag_web())
        banker, research, web = banker_json['body'], research_json['body'], web_json['body']
        logger.info('Тексты до объединения ответов:')
        logger.info(f'{banker}')
        logger.info(f'{web}')
        logger.info(f'{research}')
        banker = extract_summarization(banker, web)
        logger.info(f'{banker}')
        response = self.format_combination_answer(banker, research)
        metadata = await self.prepare_reports_data(research, research_json.get('metadata'))
        return {'body': response, 'metadata': metadata}

    async def prepare_reports_data(
            self,
            answer: str,
            metadata: dict[str, list[dict[str, str]]] | None
    ) -> dict[str, list[dict[str, str | int]]] | None:
        """
        Подготавливает данные отчетов, добавляя к ним id отчета.

        :param answer:      Ответ от Рага.
        :param metadata:    Исходные метаданные.
        :return:            Обновленные метаданные с id отчетов.
        """
        if answer in self.RAG_BAD_ANSWERS or not metadata or 'reports_data' not in metadata:
            return

        reports_data = metadata['reports_data']
        has_ids = False
        for report in reports_data:
            research_id = await research_db.get_research_id_by_report_id(report.get('report_id'))
            if research_id:
                has_ids = True
                report['research_id'] = research_id

        if has_ids:
            metadata['reports_data'] = reports_data
        else:
            metadata.pop('reports_data')
        return metadata

    def format_combination_answer(self, banker: str, research: str) -> str:
        """
        Форматирование, комбинация ответов от рага по новостям и рага рисерч.

        :param banker:    Ответ от рага по новостям.
        :param research:  Ответ от рага рисерч.
        :return:          Комбинированный ответ.
        """
        if banker == research == texts_manager.RAG_ERROR_ANSWER:
            return texts_manager.RAG_ERROR_ANSWER

        response = ''
        if banker not in self.RAG_BAD_ANSWERS:
            response += banker
        if research not in self.RAG_BAD_ANSWERS:
            response += texts_manager.RAG_RESEARCH_SUFFIX.format(answer=research)
        return response.strip() or DEFAULT_RAG_ANSWER
