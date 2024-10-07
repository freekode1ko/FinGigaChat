"""Класс с интернет ретривером"""

import asyncio
import re

from langchain_community.chat_models import GigaChat
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper

from configs.config import *
from configs.text_constants import *
from format import format_answer


class WebRetriever:
    """Класс с цепочкой для генерации ответа с аугментацией данных из поиска DuckDuckGo"""

    def __init__(self, logger):
        self.model = GigaChat(verbose=True,
                              credentials=GIGA_CREDENTIALS,
                              scope=GIGA_SCOPE,
                              model=GIGA_MODEL,
                              verify_ssl_certs=False,
                              profanity_check=False,
                              temperature=0.00001
                              )
        self.search_engine = DuckDuckGoSearchAPIWrapper(region='ru-ru')
        self.logger = logger

    def _get_answer_giga(self, system_prompt: str, text: str) -> str:
        """
        Получение ответа от GigaChat.

        :param system_prompt: Системный промпт.
        :param text: Текст запроса.
        :return: Ответ от GigaChat.
        """
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Запрос: {text}"}]
        response = self.model.invoke(messages)
        return response.content

    async def _aget_answer_giga(self, system_prompt: str, text: str) -> str:
        """
        Асинхронное получение ответа от GigaChat.

        :param system_prompt: Системный промпт.
        :param text: Текст запроса.
        :return: Ответ от GigaChat.
        """
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Запрос: {text}"}]
        response = await self.model.ainvoke(messages)
        return response.content

    @staticmethod
    def _prepare_context_duckduck(result_search: dict) -> tuple[str, dict[str, str]]:
        """
        Подготавливает результат, возвращаемый duckduck движком, для подачи в LLM.

        :param result_search: Возвращаемый результат от ретривера в json формате.
        :return: Строка для подачи в LLM, словарь с маппингом ссылок.
        """
        link_dict = {}
        parsed_answer = ''
        for i, result in enumerate(result_search):
            link_dict[f'<{i}>'] = result['link']
            context = ' '.join(f'{tag}: {result[tag]}' for tag in
                               filter(lambda x: x not in ('date', 'source', 'link'), result.keys()))
            context += f" link: <{i}> \n"
            parsed_answer += context
        return parsed_answer, link_dict

    @staticmethod
    def _post_processing_duckduck(raw_answer: str, link_dict: dict[str, str]) -> str:
        """
        Заменяет токены ссылок на реальные ссылки и добавляет в конце ответа техническое сообщение.

        :param: raw_answer. Сырой ответ LLM.
        :param: link_dict. Словарь с маппингом токенов ссылок обратно.
        :return: Строка с готовым ответом.
        """
        rep = dict((re.escape(k), v) for k, v in link_dict.items())
        pattern = re.compile("|".join(rep.keys()))
        post_processed_answer = pattern.sub(lambda x: rep[re.escape(x.group(0))], raw_answer)
        return post_processed_answer + '\n\n' + GIGA_WATERMARK

    @staticmethod
    def _change_answer_to_default(answer: str, default_answer: str = DEFAULT_ANSWER) -> str:
        """
        Ловит плохой ответ гигачата и заменяет его на дефолтную заглушку

        :param answer: Гигачата.
        :param: default_answer. Ответ, который будет использован в случае плохого ответа
        """
        return default_answer if re.search(BAD_ANSWER, answer) else answer

    async def _aanswer_chain(self,
                             question: str,
                             n_retrieved: int = N_NARROW_ANSWER,
                             output_format: str = "default") -> str:
        """
        Цепочка с продвинутым форматированием источников.

        :param: question. Запрос пользователя.
        :param: n_retrieved. Количество документов, которые будут использоваться для формирования ответа.
        :param: output_format. Формат ответа. Принимает строку "default" или "tg".
        :return: Ответ с учетом поиска в интернете с форматированием ссылок.
        """
        contexts = self.search_engine.results(question, max_results=n_retrieved)
        prepared_context, link_dict = self._prepare_context_duckduck(contexts)
        raw_answer = await self._aget_answer_giga(QNA_WITH_REFS_SYSTEM, QNA_WITH_REFS_USER.format(
            question=question, context=prepared_context))
        answer = self._post_processing_duckduck(raw_answer=raw_answer, link_dict=link_dict)
        answer = self._change_answer_to_default(answer)
        if output_format == "tg":
            answer = format_answer(answer, list(link_dict.values()))
        return answer

    async def aget_answer(self, query: str, output_format: str = 'default') -> str:
        """
        Формирование ответа на запрос с помощью нескольких цепочек.

        :param: query. Запрос пользователя.
        :param: output_format. Формат ответа. Принимает строку "default" или "tg".
        :return: Самый широкий ответ из нескольких цепочек.
        """
        tasks = [
            self._aanswer_chain(query, N_WIDE_ANSWER, output_format),
            self._aanswer_chain(query, N_NORMAL_ANSWER, output_format),
            self._aanswer_chain(query, N_NARROW_ANSWER, output_format)
        ]
        answers = await asyncio.gather(*tasks)
        final_answer = next(filter(lambda x: x not in [DEFAULT_ANSWER], answers), DEFAULT_ANSWER)
        self.logger.info(f"Обработан запрос: {query}, с ответом: {final_answer}")
        return final_answer
