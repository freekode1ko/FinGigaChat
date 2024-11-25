from fastapi import APIRouter, Request, Depends, Response
from fastapi import status

from api.v1.quotation.schemas import ExchangeSectionData, DashboardSubscriptions, DashboardGraphData
from api.v1.quotation.service import *
from constants import constants
from db import models
from db.database import get_async_session


router = APIRouter(tags=['quotation'])


@router.get('/popular')
async def popular_dashboard(session: AsyncSession = Depends(get_async_session)) -> ExchangeSectionData:
    """Специальный дашборд с популярными инструментами из разных секций"""
    return await get_special_dashboard(session)


@router.get('/dashboard')
async def dashboard_quotation(request: Request) -> ExchangeSectionData:
    """Общий дашборд не для авторизованных пользователей"""

    beautiful_dashboard = {
        # Name : format
        '12': models.SizeEnum.TEXT,
    }

    return ExchangeSectionData(
        sections=[
            *(await get_quotation_from_fx()),
            await get_quotation_from_eco(),
            await get_quotation_from_bonds(),
            await get_quotation_from_commodity(),
        ]
    )


@router.get('/dashboard/{user_id}')
async def personal_dashboard_quotation(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> ExchangeSectionData:
    """Данные для пользовательского дашборда"""
    return await get_dashboard(session, user_id)


@router.get('/dashboard/{user_id}/subscriptions')
async def get_personal_dashboard(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> DashboardSubscriptions:
    """Получить пользовательские подписки"""

    return await get_user_subscriptions(session, user_id)


@router.put(
    '/dashboard/{user_id}/subscriptions',
    status_code=status.HTTP_202_ACCEPTED,
    response_class=Response
)
async def update_personal_dashboard(
        user_id: int,
        subs_data: DashboardSubscriptions,
        session: AsyncSession = Depends(get_async_session),
) -> None:
    """Обновить пользовательские подписки"""

    return await update_user_subscriptions(session, user_id, subs_data)

@router.get('/dashboard/data/{quote_id}')
async def dashboard_quotation(
        quote_id: int,
        start_date: str | None = None,
        end_date: str | None = None,
        session: AsyncSession = Depends(get_async_session)
) -> DashboardGraphData:
    """Данные для графиков Quotes"""
    start_date = (
        datetime.datetime.strptime(start_date, constants.BASE_DATE_FORMAT)
        if start_date is not None
        else datetime.datetime.now() - datetime.timedelta(days=365)
    )
    end_date = datetime.datetime.strptime(end_date, constants.BASE_DATE_FORMAT) if end_date is not None else datetime.datetime.now()

    return await get_graph_data(session, quote_id, start_date, end_date)
