import datetime
import math

import sqlalchemy as sa
from dateutil.relativedelta import *


from constants.constants import bonds_names, commodity_pricing_names, metals_pricing_names
from db.database import async_session
from db.models import Exc, ExcType
from .schemas import SectionData, DataItem, Param


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
                        value=float(next(filter(lambda x: x[0] == i['name_db'], result_bonds))[5][:-1])
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
