"""Файл с константами для quotes"""
from db.models import Research

MENU = 'quotes_menu'
END_MENU = 'end_quotes_menu'

FX = 'fx'
FI = 'fi'
EQUITY = 'equity'
COMMODITIES = 'commodities'
ECO = 'eco'

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

RESEARCH_REPORTS = {
    'fx': [
        {
            'section_name': 'Валютный рынок и процентные ставки',
            'type_name': 'Ежемесячный обзор по мягким валютам'
        },
        {
            'section_name': 'Валютный рынок и процентные ставки',
            'type_name': 'Ежемесячный обзор по юаню'
        },
        {
            'section_name': 'Валютный рынок и процентные ставки',
            'type_name': 'Ежедневные обзоры',
            'count': 2
        },
    ],
    'fi-ofz': [
        {
            'section_name': 'Валютный рынок и процентные ставки',
            'type_name': 'Еженедельный обзор по процентным ставкам'
        },
        {
            'section_name': 'Валютный рынок и процентные ставки',
            'type_name': 'Ежедневные обзоры',
            'count': 2
        },
    ],
    'rates': [
        {
            'section_name': 'Экономика РФ',
            'type_name': 'Экономика РФ',
            'condition': Research.header.ilike('%экономика россии. ежемесячный обзор%')
        },
        {
            'section_name': 'Экономика РФ',
            'type_name': 'Экономика РФ',
            'condition': Research.header.notilike('%ежемесячный%'),
        },
    ],
    'comm':
        {
            'section_name': 'Сырьевые товары',
            'type_name': 'Сырьевые товары'
        }
}


MONTH_NAMES_DICT = {
    1: 'янв',
    2: 'фев',
    3: 'мар',
    4: 'апр',
    5: 'мая',
    6: 'июн',
    7: 'июл',
    8: 'авг',
    9: 'сен',
    10: 'окт',
    11: 'нояб',
    12: 'дек'
}
