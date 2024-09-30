from fastapi import APIRouter, Request, Depends, Response
from fastapi import status

from api.v1.quotation.schemas import ExchangeSectionData, DashboardSubscriptions, DashboardGraphData, SubscriptionSection, \
    SubscriptionItem, SizeEnum as SubscriptionSizeEnum, GraphData
from api.v1.quotation.service import *
from db import models
from db.database import get_async_session
from utils.quotes import view as quotes_view, updater as quotes_updater

router = APIRouter(tags=['quotation'])


@router.get('/popular')
async def popular_quotation(request: Request) -> ExchangeSectionData:
    return ExchangeSectionData(
        sections=(await get_quotation_from_fx()),
    )


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
    # Execute the query asynchronously
    stmt = await session.execute(
        sa.select(models.QuotesSections, models.Quotes, models.UsersQuotesSubscriptions)
        .select_from(models.Quotes)
        .join(models.QuotesSections)
        .join(models.UsersQuotesSubscriptions)
        .filter(models.UsersQuotesSubscriptions.user_id == user_id)
    )
    quotes_and_sections_subs = stmt.mappings().fetchall()

    # Prepare sections data
    sections = []
    for section in set(x['QuotesSections'] for x in quotes_and_sections_subs):
        data_items = []
        for quote_and_section in quotes_and_sections_subs:
            if quote_and_section['QuotesSections'].name == section.name:
                if quote_and_section['Quotes'].last_update.date() != datetime.date.today():  # TODO FIXME
                    update_func = getattr(quotes_updater, quote_and_section['Quotes'].update_func, None)
                    await update_func(quote_and_section['Quotes'], session)

                params = []
                data_item_value = None
                for param_name, param_func in section.params.items():
                    get_func = getattr(quotes_view, param_func, None)
                    value = await get_func(quote_and_section['Quotes'], session)
                    if param_name == '_value':
                        data_item_value = value
                        continue
                    if get_func is not None:
                        params.append(Param(name=param_name, value=value))

                data_items.append(
                    DataItem(
                        value=data_item_value,
                        quote_id=quote_and_section['Quotes'].id,
                        name=quote_and_section['Quotes'].name,
                        view_type=quote_and_section['UsersQuotesSubscriptions'].view_size,
                        image_path='123',
                        params=params
                    )
                )
        sections.append(
            SectionData(
                section_name=section.name,
                section_params=[str(_) for _ in section.params.keys()],
                data=data_items
            )
        )
    return ExchangeSectionData(sections=sections)

    # return ExchangeSectionData(
    #     sections=[
    #         SectionData(
    #             section_name=section.name,
    #             section_params=[str(_) for _ in section.params.keys()],
    #             data=[
    #                 DataItem(
    #                     quote_id=quote_and_section['Quotes'].id,
    #                     name=quote_and_section['Quotes'].name,
    #                     view_type=quote_and_section['UsersQuotesSubscriptions'].view_size,
    #                     image_path='123',
    #                     params=[
    #                         Param(
    #                             name=param_name,
    #                             value=(await get_func(quote_and_section['Quotes'], session))
    #                         )
    #                         for param_name, param_func in section.params if (get_func := getattr(quote_view, param_func, None)) is not None
    #                     ]
    #                 )
    #                 for quote_and_section
    #                 in quotes_and_sections_subs if quote_and_section['QuotesSections'].name == section
    #             ],
    #         )
    #         for section
    #         in set(x['QuotesSections'] for x in quotes_and_sections_subs)
    #     ]
    # )


@router.get('/dashboard/{user_id}/subscriptions')
async def get_personal_dashboard(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> DashboardSubscriptions:
    """Получить пользовательские подписки"""
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
                    await session.delete(quote)
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
async def dashboard_quotation(
        quote_id: int,
        start_date: str | None = None,
        end_date: str | None = None,
        session: AsyncSession = Depends(get_async_session)
) -> DashboardGraphData:
    """Данные для графиков Quotes"""
    print('$'*20)
    start_date = (
        datetime.datetime.strptime(start_date, '%d.%m.%Y').date()
        if start_date is not None
        else datetime.date.today() - datetime.timedelta(days=365)
    )
    end_date = datetime.datetime.strptime(start_date, '%d.%m.%Y').date() if end_date is not None else datetime.date.today()

    stmt = await session.execute(
        sa.select(models.QuotesValues)
        .filter_by(quote_id=quote_id)
        .order_by(models.QuotesValues.date.desc())
        .where(models.QuotesValues.date.between(start_date, end_date))
    )
    quote_data = stmt.scalars().fetchall()
    return DashboardGraphData(
        id=quote_id,
        data=[
            GraphData(
                date=quote.date,
                value=quote.value,
                open=quote.open,
                close=quote.close,
                high=quote.high,
                low=quote.low,
                # volume=quote_data.volume,
            ) for quote in quote_data
        ]
    )
