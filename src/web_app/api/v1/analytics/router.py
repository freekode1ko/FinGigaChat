"""API для работы аналитики CIB"""
from typing import Optional

from faker import Faker
from fastapi import APIRouter
from starlette import status

from api.v1.analytics.schemas import AnalyticsMenu, AnalyticsElement
from constants.constants import BASE_DATE_FORMAT

router = APIRouter(tags=["analytics"])


@router.get("/menu")
async def get_menu() -> AnalyticsMenu:
    """Получить меню аналитики для отображения во фронтенде"""
    fake = Faker()

    def generate_menu(depth) -> AnalyticsMenu:
        if depth <= 1:
            return AnalyticsMenu(
                title=fake.sentence(nb_words=6),
                analytics_menu_id=fake.unique.random_int(min=1, max=999999),
            )

        return AnalyticsMenu(
            title=fake.sentence(nb_words=6),
            analytics_menu_id=fake.unique.random_int(min=1, max=999999),
            nearest_menu=[generate_menu(depth - fake.random_int(min=1, max=depth)) for _ in range(fake.random_int(min=3, max=5))]
        )

    return generate_menu(5)


@router.get("/section/{section_id}")
async def get_sections(section_id: int, page: Optional[int] = 1, size: Optional[int] = 10) -> list[AnalyticsElement]:
    """Получить секции аналитики для отображения во фронтенде"""

    fake = Faker()
    return [AnalyticsElement(
        analytic_id=fake.unique.random_int(min=1, max=999999),
        section=fake.sentence(nb_words=2),
        title=fake.sentence(nb_words=10),
        text=fake.text(max_nb_chars=500),
        date=fake.date_between(start_date='-2y', end_date='today').strftime(BASE_DATE_FORMAT)
    ) for _ in range(10)]


@router.post('/send', status_code=status.HTTP_202_ACCEPTED)
async def send_analytics_reports_to_user(user_id: int, report_id: str):
    """Отправить отчеты с аналитикой"""
    return None
