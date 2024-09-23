"""Класс с интернет ретривером"""

import re

from langchain.chat_models import GigaChat
from langchain_community.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper

from configs.config import GIGA_MODEL, \
    GIGA_SCOPE, \
    GIGA_CREDENTIALS, \
    N_NARROW_ANSWER
from configs.prompts import QNA_WITH_REFS_SYSTEM, QNA_WITH_REFS_USER, DEFAULT_ANSWER, BAD_ANSWER


class Chain:

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
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Запрос: {text}"}]
        response = self.model.invoke(messages)
        content = response.content
        return content

    async def _aget_answer_giga(self, system_prompt: str, text: str) -> str:
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": f"Запрос: {text}"}]
        response = await self.model.ainvoke(messages)
        content = response.content
        return content

    @staticmethod
    def _prepare_context_duckduck(result_search: dict) -> tuple[str, dict[str, str]]:
        """
        Подготавливает результат, возвращаемый duckduck движком, для подачи в LLM.
        ::param: Возвращаемый результат от ретривера в json формате.
        :return: Строка для подачи в LLM, словарь с маппингом ссылок.

        """
        link_dict = {}
        parsed_answer = ''
        for i, result in enumerate(result_search):
            link_dict[f'<{i}>'] = result['link']
            context = ' '.join(f'{tag}: {result[tag]}' for tag in
                               list(filter(lambda x: x not in ['date', 'source', 'link'], result.keys())))
            context += f" link: <{i}> \n"
            parsed_answer += context
        return parsed_answer, link_dict

    @staticmethod
    def _post_processing_duckduck(raw_answer: str, link_dict: dict[str, str]) -> str:
        """
        Подготавливает сырой ответ LLM для возвращению пользователю.
        :param: raw_answer. Сырой ответ LLM.
        :param: link_dict. Словарь с маппингом токенов ссылок обратно.
        :return: Строка с готовым ответом.

        """
        rep = dict((re.escape(k), v) for k, v in link_dict.items())
        pattern = re.compile("|".join(rep.keys()))
        post_processed_answer = pattern.sub(lambda x: rep[re.escape(x.group(0))], raw_answer)
        return post_processed_answer

    @staticmethod
    def _change_answer_to_default(answer: str, default_answer: str = DEFAULT_ANSWER):
        """
        Ловит плохой ответ гигачата и заменяет его на дефолтную заглушку

        """
        if re.search(BAD_ANSWER, answer):
            return default_answer
        return answer

    async def aanswer_chain(self, question: str, n_retrieved: int = N_NARROW_ANSWER) -> str:
        """
        Цепочка с продвинутым форматированием источников.
        :param: question. Запрос пользователя.
        :param: n_retrieved. Количество документов, которые будут использоваться для формирования ответа.
        :return: Ответ с учетом поиска в интернете с форматированием ссылок.

        """
        contexts = self.search_engine.results(question, max_results=n_retrieved)
        prepared_context, link_dict = self._prepare_context_duckduck(contexts)
        raw_answer = await self._aget_answer_giga(QNA_WITH_REFS_SYSTEM, QNA_WITH_REFS_USER.format(
            question=question, context=prepared_context))
        answer = self._post_processing_duckduck(raw_answer=raw_answer, link_dict=link_dict)
        return self._change_answer_to_default(answer)
