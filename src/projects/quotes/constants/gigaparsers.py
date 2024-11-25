"""Константы для работы с котировками от GigaParsers"""
import re


# API URL
GIGAPARSERS_API = 'https://gigaparsers.ru/api/get_quotes'


# Правила для каждой секции:
#     pattern (re.Pattern): Скомпилированная регулярка для поиска нужного правила
#     get_section_name (callable): Название секции (по названию котировки)
#     section_params (dict[str, str]): Параметры секции
#     value_fields (list[str] | None): Поля с полезной нагрузкой (доходность, цена и т.д.)
#     field_mapping (dict[str, str] | None): Маппинг значений от источника на нашу БД
GIGAPARSERS_RULES = {
    'cbr': [
        {
            'pattern': re.compile(r'^(?P<quote>Инфляция|Ключевая ставка ЦБ|RUONIA)$'),
            'get_section_name': lambda m: 'Макроэкономика (ЦБ)',
            'section_params': {'_value': 'get_quote_last', '%изм': 'get_quote_delta_param'},
            'value_fields': ['value'],
            'field_mapping': {
                'value': 'value',
            },
        },
    ],
    'investing': [
        {
            'pattern': re.compile(r'^(?P<quote>.+\s(?:\d+-летние|годовые))$'),
            'get_section_name': lambda m: 'Облигации (Investing)',
            'section_params': {'_value': 'get_quote_last', '%изм': 'get_quote_delta_param'},
            'value_fields': ['Доходность'],
            'field_mapping': {
                'Доходность': 'value',
            },
        },
        {
            'pattern': re.compile(r'^INVESTING:(?P<quote>[A-Z]{3}/[A-Z]{3}):[A-Z]{3}$'),
            'get_section_name': lambda m: 'Валютные пары (Investing)',
            'section_params': {'_value': 'get_quote_last', '%изм': 'get_quote_delta_param'},
            'value_fields': ['C', 'O', 'H', 'L'],
            'field_mapping': {
                'C': 'close',
                'O': 'open',
                'H': 'high',
                'L': 'low',
            },
        },
        {
            'pattern': re.compile(r'^INVESTING:(?P<quote>.+):USD$'),
            'get_section_name': lambda m: 'Сырьевые товары (Investing)',
            'section_params': {'_value': 'get_quote_last', '%изм': 'get_quote_delta_param'},
            'value_fields': ['C', 'O', 'H', 'L'],
            'field_mapping': {
                'C': 'close',
                'O': 'open',
                'H': 'high',
                'L': 'low',
            },
        },
    ],
    'sgx': [
        {
            'pattern': re.compile(r'^SGX:(?P<quote>.+):USD$'),
            'get_section_name': lambda m: 'Фьючерсы (SGX)',
            'section_params': {'_value': 'get_quote_last', '%изм': 'get_quote_delta_param'},
            'value_fields': ['C', 'O', 'H', 'L', 'V'],
            'field_mapping': {
                'C': 'close',
                'O': 'open',
                'H': 'high',
                'L': 'low',
                'V': 'volume',
            },
        },
    ],
    'tradingeconomics': [
        {
            'pattern': re.compile(
                r'^(?P<category>(Energy|Index|Metals|Agricultural|Industrial|Electricity|Livestock))_(?P<quote>.+)$'
            ),
            'get_section_name': lambda m: {
                'Energy': 'Энергетика (TradingEconomics)',
                'Index': 'Индексы (TradingEconomics)',
                'Metals': 'Металлы (TradingEconomics)',
                'Agricultural': 'Сельское хозяйство (TradingEconomics)',
                'Industrial': 'Промышленность (TradingEconomics)',
                'Electricity': 'Электроэнергетика (TradingEconomics)',
                'Livestock': 'Животноводство (TradingEconomics)',
            }[m.group('category')],
            'section_params': {'_value': 'get_quote_last', '%изм': 'get_quote_delta_param'},
            'value_fields': ['Price'],
            'field_mapping': {
                'Price': 'value',
            },
        },
        {
            'pattern': re.compile(r'^Country_(?P<quote>.+)$'),
            'get_section_name': lambda m: 'Макроэкономика (TradingEconomics)',
            'section_params': {'_value': 'get_quote_last', '%изм': 'get_quote_delta_param'},
            'value_fields': ['Last'],
            'field_mapping': {
                'Last': 'value',
            },
        },
        # Пока здесь приходят битые данные
        # {
        #     'pattern': r'^(?P<category>Loan Prime Rate 1Y)_(?P<quote>Actual|Consensus|Previous|TEForecast)$',
        #     'get_section_name': lambda m: 'Loan Prime Rate 1Y (TradingEconomics)',
        #     'section_params': {'_value': 'get_quote_last', '%изм': 'get_quote_delta_param'},
        #     'value_fields': None,
        #     'field_mapping': None,
        # },
    ],
}
