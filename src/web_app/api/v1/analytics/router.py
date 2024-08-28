"""API для работы аналитики CIB"""
from typing import Optional

from fastapi import APIRouter
from starlette import status

from api.v1.analytics.schemas import AnalyticsMenu, AnalyticsElement

router = APIRouter(tags=["analytics"])


@router.get("/menu")
async def get_menu() -> AnalyticsMenu:
    """Получить меню аналитики для отображения во фронтенде"""
    pass

@router.get("/section/{section_id}")
async def get_sections(section_id: int, page: Optional[int] = 1, size: Optional[int] = 10) -> list[AnalyticsElement]:
    """Получить секции аналитики для отображения во фронтенде"""
    pass


@router.post('/send', status_code=status.HTTP_202_ACCEPTED)
async def send_analytics_reports_to_user(user_id: int, report_id: str):
    """Отправить отчеты с аналитикой"""
    pass

