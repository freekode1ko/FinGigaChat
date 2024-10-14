from typing import Optional

import sqlalchemy as sa

from api.v1.news.schemas import News, NewsItem, NewsTypeEnum
from constants.constants import CLIENT_SCORE_ARTICLE, BASE_DATE_FORMAT
from db.database import async_session
from db.models import Article, RelationClientArticle, Research, ResearchResearchType, ResearchType, ResearchSection


async def get_news_from_article(page: Optional[int], size: Optional[int]) -> News:
    async with async_session() as session:
        stmt = (
            sa.select(Article, )
            .join(RelationClientArticle)
            .where(RelationClientArticle.client_score > CLIENT_SCORE_ARTICLE)
            .order_by(Article.date.desc())
        )
        if page is not None and size is not None:
            stmt = stmt.offset((page - 1) * size).limit(size)

        result = await session.scalars(stmt)
    return News(
        news=[
            NewsItem(
                section=article.date.strftime(BASE_DATE_FORMAT),
                title=article.title,
                text=article.text_sum,
                date=article.date.strftime(BASE_DATE_FORMAT),
            ) for article in result
        ]
    )

async def get_cib_news(research_type_id) -> News:
    async with async_session() as session:
        research_type = await session.get(ResearchType, research_type_id)
        research_section = await session.get(ResearchSection, research_type.research_section_id)
        stmt = (
            sa.select(
                Research.header, Research.text, Research.publication_date, Research.report_id)
            .select_from(ResearchResearchType)
            .join(Research, Research.id == ResearchResearchType.research_id)
            .filter(ResearchResearchType.research_type_id == research_type_id)
            .order_by(Research.publication_date.desc())
            .offset(0).limit(10)
        )
        result = await session.execute(stmt)
        result = result.mappings().all()

    return News(
        news=[
            NewsItem(
                section=research_section.name,
                title=research['header'],
                text=research['text'],
                date=research['publication_date'].strftime(BASE_DATE_FORMAT),
                news_type=NewsTypeEnum.cib,
                news_id=research['report_id']
            ) for research in result
        ]
    )