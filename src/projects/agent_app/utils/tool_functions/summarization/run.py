"""Суммаризация новостей по названию клиента"""

import sqlalchemy as sa
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from db import models
from utils.tool_functions.fuzzy_search import FuzzyAlternativeNames
from utils.tool_functions.session import async_session
from utils.tool_functions.preparing_meeting.config import MESSAGE_RUN_NEWS, DEBUG_GRAPH
from utils.tool_functions.tool_prompts import SUMMARIZATION_SYSTEM, SUMMARIZATION_USER
from utils.tool_functions.utils import get_answer_llm, send_status_message_for_agent, get_model


@tool
async def get_news_by_name(name: str, config: RunnableConfig):
    """Возвращает текст с суммаризированными инфоповодами по компании по заданному названию компании.

    Args:
        name (str): только название компании в именительном падеже.
    return:
        (str): Текст с новостями по компании.
    """
    if DEBUG_GRAPH:
        print(f'Вызвана функция get_news_by_name с параметром: {name}')

    await send_status_message_for_agent(config, MESSAGE_RUN_NEWS)

    limit = 10
    fuzzy_searcher = FuzzyAlternativeNames()
    clients_id = await fuzzy_searcher.find_subjects_id_by_name(
        name,
        subject_types=[models.ClientAlternative],
        score=95,
    )

    async with async_session() as session:
        client_articles = await session.execute(
            sa.select(models.Article.text_sum)
            .join(models.RelationClientArticle)
            .filter(models.RelationClientArticle.client_id == clients_id[0])
            .order_by(models.Article.date)
            .limit(limit)
        )

    result = client_articles.scalars().all()

    llm = get_model()
    text = await get_answer_llm(llm, SUMMARIZATION_SYSTEM, SUMMARIZATION_USER, '\n'.join(result))

    return text
