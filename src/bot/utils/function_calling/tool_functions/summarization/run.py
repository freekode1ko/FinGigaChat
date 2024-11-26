from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from db import models
from db.database import async_session
from module.fuzzy_search import FuzzyAlternativeNames
import sqlalchemy as sa


@tool
async def get_news_by_name(name: str, config: RunnableConfig):
    """Возвращает пользователю текст с новостями по компании по заданному названию компании.

    Args:
        name (str): только название компании в именительном падеже.
    return:
        (str): Текст с новостями по компании.
    """
    limit = 10
    fuzzy_searcher = FuzzyAlternativeNames()
    clients_id = await fuzzy_searcher.find_subjects_id_by_name(
        name,
        subject_types=[models.ClientAlternative],
        score=95,
    )
    if clients_id:
        client_id = clients_id[0]
    else:
        return 'Ничего не найдено'
    async with async_session() as session:
        client_articles = await session.execute(
            sa.select(models.Article.text_sum)
            .join(models.RelationClientArticle)
            .filter(models.RelationClientArticle.client_id == client_id)
            .order_by(models.Article.date)
            .limit(limit)
        )
    result = client_articles.scalars().all()
    return result
