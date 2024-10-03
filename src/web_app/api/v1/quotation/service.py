import datetime
import math

import sqlalchemy as sa
from dateutil.relativedelta import *
from sqlalchemy.ext.asyncio import AsyncSession

from constants.constants import bonds_names, commodity_pricing_names, metals_pricing_names
from db import models
from db.database import async_session
from db.models import Exc, ExcType
from utils.quotes import view as quotes_view
from .schemas import SectionData, DataItem, Param, ExchangeSectionData, DashboardSubscriptions, SubscriptionSection, SubscriptionItem, \
    SizeEnum as SubscriptionSizeEnum, DashboardGraphData, GraphData


async def get_quotation_from_fx() -> list[SectionData]:
    async with async_session() as session:
        sel = (
            sa.select(
                sa.func.json_agg(
                    sa.func.json_build_array(
                        Exc.name,
                        Exc.value
                    )
                ),
                ExcType.name
            )
            .select_from(Exc)
            .join(ExcType)
            .group_by(ExcType.name))
        result = await session.execute(sel)
        result = result.all()

    sections = []
    for data, section_name in result:
        section = SectionData(
            section_name=section_name,
            section_params=['%день'],
            data=[],
        )

        for name, value in data:
            try:
                value = float(value)
            except (ValueError, TypeError):
                value = None

            section.data.append(
                DataItem(
                    name=name,
                    value=value,
                    params=[
                        Param(
                            name='%день',
                            value=None
                        ),
                    ]
                )
            )
        sections.append(section)
    return sections


async def get_quotation_from_eco() -> SectionData:
    async with async_session() as session:
        sel = sa.text('SELECT * FROM eco_stake')
        result = await session.execute(sel)
        result_eco = result.all()

        sel = sa.text('SELECT * FROM eco_rus_influence')
        result = await session.execute(sel)
        result_infl = result.all()

    infl_mounth = datetime.date.today() - relativedelta(months=1)
    infl_mounth = f'{infl_mounth.month}.{infl_mounth.year}'
    infl = float(next(filter(lambda x: str(x[0]) == infl_mounth, result_infl))[2])

    # Раскомментировать тут и ниже если Макс опять захочет узнать изменение инфляции
    # infl_before = float(next(filter(lambda x: str(x[0]) == infl_mounth_before, result_infl))[2])
    # infl_mounth_before = datetime.date.today() - relativedelta(months=2)
    # infl_mounth_before = f'{infl_mounth_before.month}.{infl_mounth_before.year}'

    section = SectionData(
        section_name='Процентные ставки и инфляция',
        section_params=[],
        data=[
            DataItem(
                name='Ключевая ставка ЦБ',
                value=float(next(filter(lambda x: x[0] == 'Текущая ключевая ставка Банка России', result_eco))[1]),
                params=[]
            ),
            DataItem(
                name='RUONIA',
                value=float(next(filter(lambda x: x[0] == 'Текущая ставка RUONIA', result_eco))[1]),
                params=[]
            ),
            DataItem(
                name='Инфляция %',
                value=float(infl),
                params=[
                    # Param(
                    #     name='м/м',
                    #     value=100 * (infl - infl_before) / infl_before
                    # ),
                ]
            )
        ]
    )
    return section


async def get_quotation_from_bonds() -> SectionData:
    async with async_session() as session:
        sel = sa.text('SELECT * FROM bonds')
        result = await session.execute(sel)
        result_bonds = result.all()

    data = []
    for i in bonds_names:
        data.append(
            DataItem(
                name=i['name'],
                value=float(next(filter(lambda x: x[0] == i['name_db'], result_bonds))[1]),
                params=[
                    Param(
                        name='%день',
                        value=float(str(next(filter(lambda x: x[0] == i['name_db'], result_bonds))[5])[:-1])
                    ),
                ]
            )
        )
    return SectionData(
        section_name='Доходность ОФЗ',
        section_params=['%день'],
        data=data
    )


async def get_quotation_from_commodity_pricing() -> list[DataItem]:
    data = []
    async with async_session() as session:
        sel = sa.text('SELECT * FROM commodity_pricing')
        result = await session.execute(sel)
        result = result.all()

    for i in commodity_pricing_names:
        data.append(
            DataItem(
                name=i['name'],
                value=None if math.isnan(value := float(next(filter(lambda x: x[2] == i['name_db'], result))[4])) else value,
                params=[
                    Param(
                        name='%мес',
                        value=None if math.isnan(
                            del_month := float(next(filter(lambda x: x[2] == i['name_db'], result))[5])) else 100 * del_month / (
                                value - del_month)

                    ),
                    Param(
                        name='%год',
                        value=None if math.isnan(del_year := next(filter(lambda x: x[2] == i['name_db'], result))[6]) else
                        100 * del_year / (value - del_year)
                    ),
                ]
            ),
        )
    return data


async def get_quotation_from_metals() -> list[DataItem]:
    data = []
    async with async_session() as session:
        sel = sa.text('SELECT * FROM metals')
        result = await session.execute(sel)
        result = result.all()

    for i in metals_pricing_names:
        di = DataItem(
            name=i['name'],
            value=float(next(filter(lambda x: x[0] == i['name_db'], result))[1]),
            params=[
                Param(
                    name='%день',
                    value=None if (val := next(filter(lambda x: x[0] == i['name_db'], result))[3]) is None else float(
                        val[:-1].replace(',', '.'))
                ),
                Param(
                    name='%нед',
                    value=None if (val := next(filter(lambda x: x[0] == i['name_db'], result))[4]) is None else float(
                        val[:-1].replace(',', '.'))
                ),
            ]
        )
        data.append(di)
    return data


async def get_quotation_from_commodity() -> SectionData:
    return SectionData(
        section_name='Commodities',
        section_params=['%мес', '%год'],
        data=[
            *(await get_quotation_from_commodity_pricing()),
            *(await get_quotation_from_metals()),
        ]
    )


async def get_dashboard(
        session: AsyncSession,
        user_id: int | None,
) -> ExchangeSectionData:
    if user_id is None:
        return None  # FIXME в будущем

    stmt = await session.execute(
        sa.select(models.QuotesSections, models.Quotes, models.UsersQuotesSubscriptions)
        .select_from(models.Quotes)
        .join(models.QuotesSections)
        .join(models.UsersQuotesSubscriptions)
        .filter(models.UsersQuotesSubscriptions.user_id == user_id)
    )
    quotes_and_sections_subs = stmt.mappings().fetchall()

    sections = []
    for section in set(x['QuotesSections'] for x in quotes_and_sections_subs):
        data_items = []
        for quote_and_section in quotes_and_sections_subs:
            if quote_and_section['QuotesSections'].name == section.name:
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
                        ticker=quote_and_section['Quotes'].ticker,
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


async def get_user_subscriptions(session: AsyncSession, user_id: int, ) -> DashboardSubscriptions:
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
                    ticker=quote_and_section['Quotes'].ticker,
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


async def update_user_subscriptions(
        session: AsyncSession,
        user_id: int,
        subs_data: DashboardSubscriptions
) -> None:
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
                    session.add(
                        models.UsersQuotesSubscriptions(
                            user_id=user_id,
                            quote_id=sub.id,
                            view_size=sub.type,
                        )
                    )
    await session.commit()


async def get_graph_data(
        session: AsyncSession,
        quote_id: int,
        start_date: datetime.date,
        end_date: datetime.date
) -> DashboardGraphData:
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
                # volume=quote_data.volume, пока что это не нужно
            ) for quote in quote_data
        ]
    )
