import datetime
import math

import sqlalchemy as sa
from dateutil.relativedelta import *
from db.models import Exc, ExcType
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse
from utils.templates import templates

from constants.constants import bonds_names, commodity_pricing_names, metals_pricing_names
from db.database import async_session
from .schemas import SectionData, DataItem, Param, ExchangeSectionData

router = APIRouter()


async def get_quotation_from_fx() -> list[SectionData]:
    ### FX

    async with async_session() as session:
        sel = sa.select(Exc.name, Exc.value, ExcType.name).select_from(Exc).join(ExcType)
        result = await session.execute(sel)
        result = result.all()

    sections = []
    for section_name in set(_[2] for _ in result):
        section = SectionData(
            section_name=section_name,
            data=[]
        )

        for name, value, _ in filter(lambda x: x[2] == section_name, result):
            try:
                value = float(value)
            except Exception:
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

    async with async_session() as session:
        sel = sa.text('SELECT * FROM eco_rus_influence')
        result = await session.execute(sel)
        result_infl = result.all()

    infl_mounth = datetime.date.today() - relativedelta(months=1)
    infl_mounth = f'{infl_mounth.month}.{infl_mounth.year}'
    infl_mounth_before = datetime.date.today() - relativedelta(months=2)
    infl_mounth_before = f'{infl_mounth_before.month}.{infl_mounth_before.year}'

    infl = float(next(filter(lambda x: str(x[0]) == infl_mounth, result_infl))[2])
    infl_before = float(next(filter(lambda x: str(x[0]) == infl_mounth_before, result_infl))[2])

    section = SectionData(
        section_name='Процентные ставки и инфляция',
        data=[
            DataItem(
                name='Ключевая ставка ЦБ',
                value=float(next(filter(lambda x: x[0] == 'Текущая ключевая ставка Банка России', result_eco))[1]),
                params=[
                    Param(
                        name='%',
                        value=None
                    ),
                ]
            ),
            DataItem(
                name='RUONIA',
                value=float(next(filter(lambda x: x[0] == 'Текущая ставка RUONIA', result_eco))[1]),
                params=[
                    Param(
                        name='%',
                        value=None
                    ),
                ]
            ),
            DataItem(
                name='Инфляция %',
                value=float(infl),
                params=[
                    Param(
                        name='м/м',
                        value=100 * (infl - infl_before) / infl_before
                    ),
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
                        name='%',
                        value=float(next(filter(lambda x: x[0] == i['name_db'], result_bonds))[5][:-1])
                    ),
                ]
            )
        )
    return SectionData(
        section_name='Доходность ОФЗ',
        data=data
    )


async def get_quotation_from_commodity() -> SectionData:
    data = []
    async with async_session() as session:
        sel = sa.text('SELECT * FROM commodity_pricing')
        result = await session.execute(sel)
        result = result.all()

    for i in commodity_pricing_names:
        data.append(
            DataItem(
                name=i['name'],
                value=None if math.isnan(val := float(next(filter(lambda x: x[2] == i['name_db'], result))[4])) else val,
                params=[
                    Param(
                        name='del мес',
                        value=None if math.isnan(val := float(next(filter(lambda x: x[2] == i['name_db'], result))[5])) else val
                    ),
                    Param(
                        name='del год',
                        value=None if math.isnan((val := next(filter(lambda x: x[2] == i['name_db'], result))[5])) else val  # FIXME
                    ),
                ]
            ),
        )

    async with async_session() as session:
        sel = sa.text('SELECT * FROM metals')
        result = await session.execute(sel)
        result = result.all()

    for i in metals_pricing_names:
        a = DataItem(
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
        data.append(a)

    return SectionData(
        section_name='Commodities',
        data=data)


@router.get('/popular')
async def popular_quotation(request: Request) -> ExchangeSectionData:
    return ExchangeSectionData(
        sections=(await get_quotation_from_fx()),
    )


@router.get('/dashboard')
async def dashboard_quotation(request: Request) -> ExchangeSectionData:
    a = ExchangeSectionData(
        sections=[
            *(await get_quotation_from_fx()),
            await get_quotation_from_eco(),
            await get_quotation_from_bonds(),
            await get_quotation_from_commodity(),
        ]
    )

    return a


@router.get("/show", response_class=HTMLResponse)
async def show_quotes(request: Request):
    return templates.TemplateResponse("quotation.html", {"request": request})
