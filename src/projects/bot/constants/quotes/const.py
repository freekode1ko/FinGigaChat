"""Файл с константами для quotes"""
from typing import Any, Optional

from pydantic import BaseModel, Field

from constants.enums import QuotesType
from db.models import Research

MENU = 'quotes_menu'
END_MENU = 'end_quotes_menu'
GET_FI_ITEM_DATA = 'get_fi_item_data'

COMMODITY_MARKS = {
    'price': 'Цена',
    'day': 'Δ День',
    'week': 'Δ Неделя',
    'month': 'Δ Месяц',
    'year': 'Δ Год'
}

COMMODITY_TABLE_ELEMENTS = (
    'Нефть WTI',
    'Нефть Urals',
    'Нефть Brent',
    'Медь',
    'Алюминий',
    'Никель',
    'Свинец',
    'Цинк',
    'Золото',
    'Серебро',
    'Палладий',
    'Платина',
    'Кобальт',
    'ЖРС (Китай)',
    'Эн. уголь',
    'Кокс. уголь'
)


class ReportParameter(BaseModel):
    """Параметры для получения CIB Research отчетов"""

    section_name: str
    type_name: str
    count: Optional[int] = 1
    format: Optional[bool] = False
    format_args: Optional[dict] = Field(default_factory=dict)
    condition: Optional[Any] = True


RESEARCH_REPORTS_PARAMETERS = {
    QuotesType.FX: [
        ReportParameter(
            section_name='Валютный рынок и процентные ставки',
            type_name='Ежемесячный обзор по мягким валютам'
        ),
        ReportParameter(
            section_name='Валютный рынок и процентные ставки',
            type_name='Ежемесячный обзор по юаню'
        ),
        ReportParameter(
            section_name='Валютный рынок и процентные ставки',
            type_name='Ежедневные обзоры',
            count=2,
            format=True,
            format_args=dict(start='Валютный рынок', end='Процентные ставки')
        ),
    ],
    QuotesType.FI: [
        ReportParameter(
            section_name='Валютный рынок и процентные ставки',
            type_name='Еженедельный обзор по процентным ставкам'
        ),
        ReportParameter(
            section_name='Валютный рынок и процентные ставки',
            type_name='Ежедневные обзоры',
            count=2,
            format=True,
            format_args=dict(start='Процентные ставки')
        )
    ],
    QuotesType.ECO: [
        ReportParameter(
            section_name='Экономика РФ',
            type_name='Экономика РФ',
            condition=Research.header.ilike('%экономика россии. ежемесячный обзор%'),
        ),
        ReportParameter(
            section_name='Экономика РФ',
            type_name='Экономика РФ',
            condition=Research.header.notilike('%ежемесячный%'),
        ),
    ],
    QuotesType.COMMODITIES: [
        ReportParameter(section_name='Сырьевые товары', type_name='Сырьевые товары', format=True),
    ]
}
