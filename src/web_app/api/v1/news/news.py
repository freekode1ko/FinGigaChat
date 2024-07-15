"""API для работы новостей"""
from datetime import datetime

import sqlalchemy as sa
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from utils.templates import templates

from db.database import async_session
from db.models import Article, RelationClientArticle

router = APIRouter()


@router.get('/')
async def get_news(page: int, size: int) -> JSONResponse:
    async with (async_session() as session):
        stmt = (
            sa.select(Article,)
            .join(RelationClientArticle)
            .where(RelationClientArticle.client_score > 3)
            .order_by(Article.date.desc())
            .offset((page - 1) * size).limit(size)
        )
        result = await session.scalars(stmt)
    data = []

    for article in result:
        data.append(
            {
                'section': article.date.strftime("%d.%m.%Y"),
                'title': article.title,
                'text': article.text_sum,
                'date': article.date.strftime("%d.%m.%Y"),
            }
        )

    return JSONResponse({'news': data,})


@router.get("/show", response_class=HTMLResponse)
async def show_news(request: Request):
    return templates.TemplateResponse("news.html", {"request": request})
