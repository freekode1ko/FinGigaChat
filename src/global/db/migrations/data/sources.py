"""
Содержит данные по подгруппам источников и сами источники
"""
groups = [
    {
        'id': 1,
        'name': 'Облигации',
        'name_latin': 'bonds',
    },
    {
        'id': 2,
        'name': 'Экономика',
        'name_latin': 'eco',
    },
    {
        'id': 3,
        'name': 'Курсы валют',
        'name_latin': 'exc',
    },
    {
        'id': 4,
        'name': 'Металлы',
        'name_latin': 'metals',
    },
    {
        'id': 5,
        'name': 'GigaParsers',
        'name_latin': 'GigaParsers',
    },
    {
        'id': 6,
        'name': 'Weekly Pulse',
        'name_latin': 'Weekly Pulse',
    },
    {
        'id': 7,
        'name': 'CIB',
        'name_latin': 'CIB',
    },
    {
        'id': 8,
        'name': 'Полианалист',
        'name_latin': 'Polyanalyst',
    },
]


sources = [
    {
        'name': 'ключевая ставка Банка России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 2,
    },
    {
        'name': 'текущая ставка RUONIA',
        'alt_names': [],
        'response_format': '[X%] - текущая ставка RUONIA',
        'source': 'https://www.cbr.ru/hd_base/ruonia',
        'source_group_id': 2,
    },
    {
        'name': 'LPR Китай',
        'alt_names': [],
        'response_format': '[X%] - LPR Китай',
        'source': 'https://tradingeconomics.com/china/interest-rate',
        'source_group_id': 2,
    },
    {
        'name': 'Ключевые ставки ЦБ',
        'alt_names': [],
        'response_format': 'Ключевые ставки ЦБ мира | Страна | Ставка | Предыдущая',
        'source': 'https://tradingeconomics.com/country-list/interest-rate',
        'source_group_id': 2,
    },
    {
        'name': 'Инфляция в России',
        'alt_names': [],
        'response_format': 'Инфляция в России | Дата | Инфляция, % г/г',
        'source': 'https://www.cbr.ru/hd_base/infl',
        'source_group_id': 2,
    },
    {
        'name': 'Облигации',
        'alt_names': [],
        'response_format': 'Лет до погашения  |  Доходность',
        'source': 'https://ru.investing.com/rates-bonds/world-government-bonds',
        'source_group_id': 1,
    },
    {
        'name': 'Медь',
        'alt_names': [],
        'response_format': 'Медь | X | X% | X% | X% | X%',
        'source': 'https://www.bloomberg.com/quote/LMCADS03:COM',
        'source_group_id': 4,
    },
    {
        'name': 'Алюминий',
        'alt_names': [],
        'response_format': 'Алюминий',
        'source': 'https://tradingeconomics.com/commodities',
        'source_group_id': 4,
    },
    {
        'name': 'ЖРС (Китай)',
        'alt_names': [],
        'response_format': 'ЖРС (Китай)',
        'source': 'https://investing.com/commodities/coal-(api2)-cif-ara-futures-historical-data',
        'source_group_id': 4,
    },
    {
        'name': 'Кокс. уголь (Au)',
        'alt_names': [],
        'response_format': 'Кокс. уголь (Au)',
        'source': 'https://www.barchart.com/futures/quotes/U7*0',
        'source_group_id': 4,
    },
    {
        'name': 'USD/RUB',
        'alt_names': [],
        'response_format': 'USD/RUB | [X]',
        'source': 'https://investing.com/currencies/usd-rub',
        'source_group_id': 3,
    },
    {
        'name': 'EUR/RUB',
        'alt_names': [],
        'response_format': 'EUR/RUB | [X]',
        'source': 'https://investing.com/currencies/eur-rub',
        'source_group_id': 3,
    },
    {
        'name': 'CNH/RUB',
        'alt_names': [],
        'response_format': 'CNH/RUB | [X]',
        'source': 'https://investing.com/currencies/cny-rub',
        'source_group_id': 3,
    },
    {
        'name': 'EUR/USD',
        'alt_names': [],
        'response_format': 'EUR/USD | [X]',
        'source': 'https://investing.com/currencies/eur-usd',
        'source_group_id': 3,
    },
    {
        'name': 'USD/CNH',
        'alt_names': [],
        'response_format': 'USD/CNH | [X]',
        'source': 'https://investing.com/currencies/usd-cnh',
        'source_group_id': 3,
    },
    {
        'name': 'Индекс DXY',
        'alt_names': [],
        'response_format': 'Индекс DXY | [X]',
        'source': 'https://investing.com/indices/usdollar',
        'source_group_id': 3,
    },
    {
        'name': 'Weekly Pulse',
        'alt_names': [],
        'response_format': 'Презентация Weekly Pulse с CIB Research',
        'source': 'https://research.sberbank-cib.com/group/guest/money',
        'source_group_id': 6,
    },
    {
        'name': 'Полианалист',
        'alt_names': [],
        'response_format': 'Полианалист',
        'source': 'ai-helper@mail.ru',
        'source_group_id': 8,
    },
]
