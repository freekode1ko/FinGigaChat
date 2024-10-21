"""API для работы новостей"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, status

from api.v1.news.schemas import News
from api.v1.news.service import get_news_from_article, get_cib_news
from constants.constants import BASE_DATE_FORMAT
from utils.bot_interaction import send_cib_report_to_user

router = APIRouter(tags=['news'])


@router.get('/')
async def get_news(page: Optional[int] = 1, size: Optional[int] = 10) -> News:
    """Получить все новости отсортированные по дате"""

    return await get_news_from_article(page, size)


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


@router.post('/send', status_code=status.HTTP_202_ACCEPTED)
async def send_news_to_user(user_id: int, news_id: str):
    await send_cib_report_to_user(user_id, news_id)
    return None
