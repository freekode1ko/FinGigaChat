from fastapi import APIRouter, Request
from starlette import status

from api.v1.quotation.schemas import ExchangeSectionData, DashboardSubscriptions, DashboardGraphData, SubscriptionSection, \
    SubscriptionItem, SizeEnum as SubscriptionSizeEnum
from api.v1.quotation.service import *
from db import models

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
    async with async_session() as session:
        stmt = await session.execute(
            sa.select(models.QuotesSections, models.Quotes)
            .select_from(models.Quotes)
            .join(models.QuotesSections)
        )
        quotes_and_sections = stmt.mappings().fetchall()

        stmt = await session.execute(
            sa.select(models.UsersQuotesSubscriptions)
            .filter(models.UsersQuotesSubscriptions.user_id == user_id)
        )
        subs = stmt.scalars().fetchall()
        users_sub_ids = list(sub.quote_id for sub in subs)

        return DashboardSubscriptions(subscription_sections=[
            SubscriptionSection(
                section_name=section_name,
                subscription_items=[
                    SubscriptionItem(
                        id=quote_and_section['Quotes'].id,
                        name=quote_and_section['Quotes'].name,
                        active=(active := bool(quote_and_section['Quotes'].id in users_sub_ids)),
                        type=(
                            next(filter(lambda x: x.quote_id == quote_and_section['Quotes'].id, subs)).view_size
                            if active
                            else SubscriptionSizeEnum.TEXT
                        ),
                    )
                    for quote_and_section
                    in quotes_and_sections if quote_and_section['QuotesSections'].name == section_name
                ]
            )
            for section_name
            in set(x['QuotesSections'].name for x in quotes_and_sections)
        ])


@router.put('/dashboard/{user_id}/subscriptions', status_code=status.HTTP_202_ACCEPTED)
async def update_personal_dashboard(user_id: int, subs_data: DashboardSubscriptions):
    """Обновить пользовательские подписки"""
    async with async_session() as session:
        stmt = await session.execute(
            sa.select(models.UsersQuotesSubscriptions)
            .filter(models.UsersQuotesSubscriptions.user_id == user_id)
        )
        user_subs = stmt.scalars().fetchall()

        for section in subs_data.subscription_sections:
            for sub in section.subscription_items:
                try:
                    quote = next(filter(lambda x: x.quote_id == sub.id, user_subs))
                    quote.view_size = sub.type
                    if sub.active:
                        quote.view_size = sub.type
                    else:
                        session.delete(quote)
                except StopIteration:
                    if sub.active:
                        # create
                        session.add(
                            models.UsersQuotesSubscriptions(
                                user_id=user_id,
                                quote_id=sub.id,
                                view_size=sub.type,
                            )
                        )
        await session.commit()


@router.get('/dashboard/data/{quote_id}')
async def dashboard_quotation(quote_id: int, start_date: str | None, end_date: str | None) -> DashboardGraphData:
    """Данные для графиков Quotes"""
    pass
