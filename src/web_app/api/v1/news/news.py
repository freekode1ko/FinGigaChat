"""API для работы новостей"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from api.v1.news.service import get_news_from_article, get_cib_news
from api.v1.news.schemas import News
from constants.constants import BASE_DATE_FORMAT

router = APIRouter()


@router.get('/')
async def get_news(page: Optional[int] = 1, size: Optional[int] = 10) -> News:
    """Получить все новости отсортированные по дате"""

    return (await get_news_from_article(page, size))


@router.get('/{quotation_id}')
async def news_for_quotation(quotation_id: int) -> News:
    article_news = await get_news_from_article(page=1, size=10)
    cib_news = await get_cib_news(quotation_id)

    return News(
        news=sorted(
            [*article_news.news, *cib_news.news],
            key=lambda x: datetime.strptime(x.date, BASE_DATE_FORMAT).date(),
            reverse=True
        )[:10],
    )
