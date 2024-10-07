"""Класс с интернет ретривером"""

import asyncio
import re

from langchain_community.chat_models import GigaChat
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from sklearn.feature_extraction.text import TfidfVectorizer

from configs.text_constants import *
from configs.config import *
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
        self.vectorizer = TfidfVectorizer()

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

    async def _deduplicate(self, result_search: list[dict]) -> list[dict]:
        """
        Проводит дедубликацию документов, которые вернулись от duckduck.

        :param result_search: Возвращаемый результат от ретривера в json формате.
        :return: Результат без дублей.
        """
        self.logger.info(f'Начало дедубликации {len(result_search)} документов.')

        for doc in result_search:
            self.logger.info(doc)
        result_search.sort(reverse=True, key=lambda x: len(x['snippet'] + x['title']))
        deduplicated_docs = list()
        deduplicated_docs_idxs = set()

        texts = [doc['title'] + doc['snippet'] for doc in result_search]
        vec_texts = self.vectorizer.fit_transform(texts)
        scores = vec_texts @ vec_texts.T  # (n_docs, n_dim) @ (n_docs, n_dim).T -> (n_docs, n_docs)

        for i in range(len(texts)):
            flag_unique_document = True
            for j in range(i):
                is_docs_similarity = scores[i, j] > DEDUPLICATION_THRESHOLD
                is_previously_added = j in deduplicated_docs_idxs
                if is_docs_similarity and is_previously_added:
                    flag_unique_document = False
                    self.logger.info(
                        f'Документы определены как дубли со скором {scores[i, j]}'
                    )
                    self.logger.info(f'Документ: {result_search[i]}')
                    self.logger.info(f'Документ: {result_search[j]}')

            if flag_unique_document:
                deduplicated_docs.append(result_search[i])
                deduplicated_docs_idxs.add(i)
        self.logger.info('Дедубликация документов завершена')

        for doc in deduplicated_docs:
            self.logger.info(doc)
        return deduplicated_docs

    async def _prepare_context_duckduck(self, result_search: list[dict]) -> tuple[str, dict[str, str]]:
        """
        Подготавливает результат, возвращаемый duckduck движком, для подачи в LLM.

        :param result_search: Возвращаемый результат от ретривера в json формате.
        :return: Строка для подачи в LLM, словарь с маппингом ссылок.
        """
        link_dict = {}
        parsed_answer = ''
        result_search = await self._deduplicate(result_search)
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
        return default_answer if re.search(BAD_ANSWER, answer.lower()) else answer

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
        prepared_context, link_dict = await self._prepare_context_duckduck(contexts)
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
