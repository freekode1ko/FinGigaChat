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
        self.model = GigaChat(base_url=GIGA_URL,
                              verbose=True,
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
        self.logger.info('Отправлен запрос в GigaChat')
        self.logger.info(f"Запрос: {text}")
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Запрос: {text}"}]
        response = self.model.invoke(messages)
        self.logger.info('Получен ответ от GigaChat')
        return response.content

    async def _aget_answer_giga(self, system_prompt: str, text: str) -> str:
        """
        Асинхронное получение ответа от GigaChat.

        :param system_prompt: Системный промпт.
        :param text: Текст запроса.
        :return: Ответ от GigaChat.
        """
        try:
            self.logger.info('Отправлен запрос в GigaChat')
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Запрос: {text}"}]
            response = await self.model.ainvoke(messages)
            self.logger.info('Получен ответ от GigaChat')
            answer = response.content
        except Exception as e:
            self.logger.error(f'Не получен ответ от гигачата по причине: {e}')
            answer = DEFAULT_ANSWER
        return answer

    async def _deduplicate(self, result_search: list[dict]) -> list[dict]:
        """
        Проводит дедубликацию документов, которые вернулись от duckduck.

        :param result_search: Возвращаемый результат от ретривера в json формате.
        :return: Результат без дублей.
        """
        self.logger.info(f'Начало дедубликации {len(result_search)} документов.')

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
        self.logger.info(f'Дедубликация документов завершена. Осталось {len(deduplicated_docs)} документов.')
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
                             n_retrieved: int = N_NARROW_ANSWER) -> tuple[str, list[str]]:
        """
        Цепочка с продвинутым форматированием источников.

        :param: question. Запрос пользователя.
        :param: n_retrieved. Количество документов, которые будут использоваться для формирования ответа.
        :return: Ответ и массив ссылок, которые были использованы в ответе.
        """
        # небольшие таймауты, чтобы не ловить rate limit от duckduck
        await asyncio.sleep((N_WIDE_ANSWER - n_retrieved) // 3)
        # TODO: добавить еще один интернет движок, потому что дак дак отваливается периодически
        try:
            contexts = self.search_engine.results(question, max_results=n_retrieved)
        except Exception as e:
            self.logger.error(f"Не получены ответы от duckduck по причине: {e}")
            return DEFAULT_ANSWER, []
        prepared_context, link_dict = await self._prepare_context_duckduck(contexts)
        raw_answer = await self._aget_answer_giga(QNA_WITH_REFS_SYSTEM, QNA_WITH_REFS_USER.format(
            question=question, context=prepared_context))
        answer = self._post_processing_duckduck(raw_answer=raw_answer, link_dict=link_dict)
        answer = self._change_answer_to_default(answer)
        return answer, list(link_dict.values())

    async def aget_answer(self, query: str, output_format: str = 'default', debug: bool = False) -> list[str]:
        """
        Формирование ответа на запрос с помощью нескольких цепочек.

        :param: query. Запрос пользователя.
        :param: output_format. Формат ответа. Принимает строку "default" или "tg".
        :param: debug. Если True, то возвращает и обычный и отформатированный ответ одновременно.
        :return: Самый широкий ответ из нескольких цепочек.
        """
        self.logger.info(f'Старт обработки запроса {query}.')
        self.logger.info('Формирование ответов с разным объемом контекста.')
        tasks = [
            self._aanswer_chain(query, N_WIDE_ANSWER),
            self._aanswer_chain(query, N_NORMAL_ANSWER),
            self._aanswer_chain(query, N_NARROW_ANSWER)
        ]
        answers = await asyncio.gather(*tasks, return_exceptions=True)
        self.logger.info('Получены ответы. Выбор лучшего из них.')
        final_answer = next(filter(lambda x: x[0] not in [DEFAULT_ANSWER], answers), DEFAULT_ANSWER)
        self.logger.info(f"Обработан запрос: {query}, с ответом: {final_answer}")
        if final_answer == DEFAULT_ANSWER:
            return [DEFAULT_ANSWER]
        if debug:
            return [final_answer[0], format_answer(final_answer[0], final_answer[1])]
        elif output_format == 'tg':
            final_answer = format_answer(final_answer[0], final_answer[1])
        return [final_answer]
