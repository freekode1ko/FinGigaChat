"""Список старых и новых источников для курсов"""

import sqlalchemy as sa

from models import models


source_group_id_subquery = sa.select(models.SourceGroup.id).where(models.SourceGroup.name_latin == 'exc').scalar_subquery()


old_data = [
    {
        'name': 'USD/RUB',
        'alt_names': '{}',
        'response_format': 'USD/RUB | [X]',
        'source': 'https://investing.com/currencies/usd-rub',
        'source_group_id': source_group_id_subquery,
        'params': None,
        'before_link': '',
    },
    {
        'name': 'EUR/RUB',
        'alt_names': '{}',
        'response_format': 'EUR/RUB | [X]',
        'source': 'https://investing.com/currencies/eur-rub',
        'source_group_id': source_group_id_subquery,
        'params': None,
        'before_link': '',
    },
    {
        'name': 'CNH/RUB',
        'alt_names': '{}',
        'response_format': 'CNH/RUB | [X]',
        'source': 'https://investing.com/currencies/cny-rub',
        'source_group_id': source_group_id_subquery,
        'params': None,
        'before_link': '',
    },
    {
        'name': 'EUR/USD',
        'alt_names': '{}',
        'response_format': 'EUR/USD | [X]',
        'source': 'https://investing.com/currencies/eur-usd',
        'source_group_id': source_group_id_subquery,
        'params': None,
        'before_link': '',
    },
    {
        'name': 'USD/CNH',
        'alt_names': '{}',
        'response_format': 'USD/CNH | [X]',
        'source': 'https://investing.com/currencies/usd-cnh',
        'source_group_id': source_group_id_subquery,
        'params': None,
        'before_link': '',
    },
    {
        'name': 'Индекс DXY',
        'alt_names': '{}',
        'response_format': 'Индекс DXY | [X]',
        'sources': 'https://investing.com/indices/usdollar',
        'source_group_id': source_group_id_subquery,
        'params': None,
        'before_link': '',
    },
]


new_data = [
    # Spot
    {
        'name': 'CNH/RUB (MOEX)',
        'alt_names': '{}',
        'response_format': 'CNH/RUB (MOEX)',
        'source': 'https://ru.tradingview.com/symbols/CNYRUB_TOM/?exchange=MOEX',
        'source_group_id': source_group_id_subquery,
        'params': {'tag': 'div', 'attrs': {'class': 'lastContainer-.+'}},
        'before_link': '',
    },
    {
        'name': 'USD/RUB (межбанк)',
        'alt_names': '{}',
        'response_format': 'USD/RUB (межбанк)',
        'source': 'https://www.finam.ru/quote/forex/usdrub/',
        'source_group_id': source_group_id_subquery,
        'params': {
            'url': 'wss://ta-streaming.finam.ru/ta/server/?command=start&protocol=5&version=tx-protocol-html5-%version%&locale=en',
            'accept_messages_handshake': 1,
            'max_recv_messages': 10,
            'message_type_key': '1',
            'searched_message_type': 222,
            'exchange_list_key': '3',
            'exchange_data_keys': ['2', 0, '3'],
            'send_messages': [
                {
                    'data_key': '1',
                    'data': [
                        {
                            'id_': 237,
                            'info': 3,
                            'quotes_list_json': '{\"1\":\"1\",\"2\":\"test_user_delay_data\"}',
                        },
                    ],
                },
                {
                    'data_key': '1',
                    'data': [
                        {
                            'id_': 2001,
                            'info': 4,
                            'quotes_list_json': '{\"1\":[{\"1\":901}]}',
                        },
                        {
                            'id_': 232,
                            'info': 5,
                            'quotes_list_json': '{\"1\":[{\"1\":901}]}',
                        },
                    ],
                },
            ],
        },
        'before_link': '',
    },
    {
        'name': 'EUR/RUB (межбанк)',
        'alt_names': '{}',
        'response_format': 'EUR/RUB (межбанк)',
        'source': 'https://www.finam.ru/quote/forex/eurrub/',
        'source_group_id': source_group_id_subquery,
        'params': {
            'url': 'wss://ta-streaming.finam.ru/ta/server/?command=start&protocol=5&version=tx-protocol-html5-%version%&locale=en',
            'accept_messages_handshake': 1,
            'max_recv_messages': 10,
            'message_type_key': '1',
            'searched_message_type': 222,
            'exchange_list_key': '3',
            'exchange_data_keys': ['2', 0, '3'],
            'send_messages': [
                {
                    'data_key': '1',
                    'data': [
                        {
                            'id_': 237,
                            'info': 3,
                            'quotes_list_json': '{\"1\":\"1\",\"2\":\"test_user_delay_data\"}',
                        },
                    ],
                },
                {
                    'data_key': '1',
                    'data': [
                        {
                            'id_': 2001,
                            'info': 4,
                            'quotes_list_json': '{\"1\":[{\"1\":66860}]}',
                        },
                        {
                            'id_': 232,
                            'info': 5,
                            'quotes_list_json': '{\"1\":[{\"1\":66860}]}',
                        },
                    ],
                },
            ],
        },
        'before_link': '',
    },
    # CB
    {
        'name': 'CNH/RUB',
        'alt_names': '{}',
        'response_format': 'CNH/RUB',
        'source': 'https://www.cbr.ru/currency_base/daily/',
        'source_group_id': source_group_id_subquery,
        'params': {'name': 'td', 'kwargs': {'string': 'CNY'}, 'children_name': 'td'},
        'before_link': '',
    },
    {
        'name': 'USD/RUB',
        'alt_names': '{}',
        'response_format': 'USD/RUB',
        'source': 'https://www.cbr.ru/currency_base/daily/',
        'source_group_id': source_group_id_subquery,
        'params': {'name': 'td', 'kwargs': {'string': 'USD'}, 'children_name': 'td'},
        'before_link': '',
    },
    {
        'name': 'EUR/RUB',
        'alt_names': '{}',
        'response_format': 'EUR/RUB',
        'source': 'https://www.cbr.ru/currency_base/daily/',
        'source_group_id': source_group_id_subquery,
        'params': {'name': 'td', 'kwargs': {'string': 'EUR'}, 'children_name': 'td'},
        'before_link': '',
    },
    # future
    {
        'name': 'CNH/RUB',
        'alt_names': '{}',
        'response_format': 'CNH/RUB',
        'source': 'https://ru.tradingview.com/symbols/MOEX-CR1%21/',
        'source_group_id': source_group_id_subquery,
        'params': {'tag': 'div', 'attrs': {'class': 'lastContainer-.+'}},
        'before_link': '',
    },
    {
        'name': 'USD/RUB',
        'alt_names': '{}',
        'response_format': 'USD/RUB',
        'source': 'https://ru.tradingview.com/symbols/MOEX-SI1%21/',
        'source_group_id': source_group_id_subquery,
        'params': {'tag': 'div', 'attrs': {'class': 'lastContainer-.+'}},
        'before_link': '',
    },
    {
        'name': 'EUR/RUB',
        'alt_names': '{}',
        'response_format': 'EUR/RUB',
        'source': 'https://ru.tradingview.com/symbols/MOEX-EU1%21/',
        'source_group_id': source_group_id_subquery,
        'params': {'tag': 'div', 'attrs': {'class': 'lastContainer-.+'}},
        'before_link': '',
    },
    # Others
    {
        'name': 'USD/CNH',
        'alt_names': '{}',
        'response_format': 'USD/CNH | [X]',
        'source': 'https://investing.com/currencies/usd-cnh',
        'source_group_id': source_group_id_subquery,
        'params': {'kwargs': {'attrs': {'data-test': 'instrument-price-last'}}, 'name': 'div'},
        'before_link': '',
    },
    {
        'name': 'EUR/USD',
        'alt_names': '{}',
        'response_format': 'EUR/USD | [X]',
        'source': 'https://investing.com/currencies/eur-usd',
        'source_group_id': source_group_id_subquery,
        'params': {'kwargs': {'attrs': {'data-test': 'instrument-price-last'}}, 'name': 'div'},
        'before_link': '',
    },
    {
        'name': 'Индекс DXY',
        'alt_names': '{}',
        'response_format': 'Индекс DXY | [X]',
        'source': 'https://investing.com/indices/usdollar',
        'source_group_id': source_group_id_subquery,
        'params': {'kwargs': {'attrs': {'data-test': 'instrument-price-last'}}, 'name': 'div'},
        'before_link': '',
    },
]
