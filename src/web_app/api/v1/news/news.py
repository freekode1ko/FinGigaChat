"""API для работы новостей"""
from typing import Optional

import sqlalchemy as sa
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse

from constants.constants import CLIENT_SCORE_ARTICLE, BASE_DATE_FORMAT
from db.database import async_session
from db.models import Article, RelationClientArticle
from utils.templates import templates


router = APIRouter()


@router.get('/')
async def get_news(page: Optional[int] = 1, size: Optional[int] = 10) -> JSONResponse:
    async with async_session() as session:
        stmt = (
            sa.select(Article,)
            .join(RelationClientArticle)
            .where(RelationClientArticle.client_score > CLIENT_SCORE_ARTICLE)
            .order_by(Article.date.desc())
            .offset((page - 1) * size).limit(size)
        )
        result = await session.scalars(stmt)
    data = []

    for article in result:
        data.append(
            {
                'section': article.date.strftime(BASE_DATE_FORMAT),
                'title': article.title,
                'text': article.text_sum,
                'date': article.date.strftime(BASE_DATE_FORMAT),
            }
        )

    return JSONResponse({'news': data,})
