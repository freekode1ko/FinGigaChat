from fastapi import APIRouter, Request
from starlette import status

from api.v1.quotation.schemas import ExchangeSectionData, DashboardSubscriptions, DashboardGraphData
from api.v1.quotation.service import *

router = APIRouter(tags=['quotation'])


@router.get('/popular')
async def popular_quotation(request: Request) -> ExchangeSectionData:
    return ExchangeSectionData(
        sections=(await get_quotation_from_fx()),
    )


@router.get('/dashboard')
async def dashboard_quotation(request: Request) -> ExchangeSectionData:
    """Общий дашборд не для авторизованных пользователей"""
    return ExchangeSectionData(
        sections=[
            *(await get_quotation_from_fx()),
            await get_quotation_from_eco(),
            await get_quotation_from_bonds(),
            await get_quotation_from_commodity(),
        ]
    )


@router.get('/dashboard/{user_id}')
async def personal_dashboard_quotation(request: Request) -> ExchangeSectionData:
    """Данные для пользовательского дашборда"""
    pass


@router.get('/dashboard/{user_id}/subscriptions')
async def get_personal_dashboard(user_id: int, ) -> DashboardSubscriptions:
    """Получить пользовательские подписки"""
    pass


@router.put('/dashboard/{user_id}/subscriptions', status_code=status.HTTP_202_ACCEPTED)
async def update_personal_dashboard(user_id: int, subs: DashboardSubscriptions):
    """Обновить пользовательские подписки"""
    pass


@router.get('/dashboard/data/{quote_id}')
async def dashboard_quotation(quote_id: int, start_date: str | None, end_date: str | None) -> DashboardGraphData:
    """Данные для графиков Quotes"""
    pass

