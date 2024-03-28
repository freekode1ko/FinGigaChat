
groups = [
    {
        'id': 1,
        'name': 'Области',
        'dropdown_flag': False,
    },
    {
        'id': 2,
        'name': 'Разделы',
        'dropdown_flag': True,
    },
    {
        'id': 3,
        'name': 'Клиенты',
        'dropdown_flag': True,
    },
]

sections = [
    {
        'id': 1,
        'name': 'Экономика',
        'research_group_id': 1,
    },
    {
        'id': 2,
        'name': 'Валютный рынок',
        'research_group_id': 2,
    },
    {
        'id': 3,
        'name': 'Отрасли',
        'research_group_id': 2,
    },
    {
        'id': 4,
        'name': 'Нефть и газ',
        'research_group_id': 3,
    },
    {
        'id': 5,
        'name': 'Металлургия',
        'research_group_id': 3,
    },
]

new_source_group = [
    {
        'id': 9,
        'name': 'Отчеты CIB Research',
        'name_latin': 'cib_research',
    },
]

research_types_sources = [
    {
        'id': 19,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
    {
        'id': 20,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
    {
        'id': 21,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
    {
        'id': 22,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
    {
        'id': 23,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
    {
        'id': 24,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
    {
        'id': 25,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
    {
        'id': 26,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
    {
        'id': 27,
        'name': 'Экономика России',
        'alt_names': [],
        'response_format': '[X%] - текущая ключевая ставка Банка России',
        'source': 'https://www.cbr.ru/hd_base/KeyRate',
        'source_group_id': 9,
    },
]

research_types = [
    {
        'name': 'Экономика',
        'description': 'Раздел экономики',
        'research_section_id': 1,
        'source_id': 19,
    },
    {
        'name': 'Валюта USD',
        'description': 'Раздел валют',
        'research_section_id': 2,
        'source_id': 20,
    },
    {
        'name': 'Валюта мира РУБ',
        'description': 'Раздел валют',
        'research_section_id': 2,
        'source_id': 21,
    },
    {
        'name': 'Нефть и газ',
        'description': 'Раздел Отрасли',
        'research_section_id': 3,
        'source_id': 22,
    },
    {
        'name': 'Металлургия',
        'description': 'Раздел Отрасли',
        'research_section_id': 3,
        'source_id': 23,
    },
    {
        'name': 'Газпром',
        'description': 'Раздел Нефть и газ',
        'research_section_id': 4,
        'source_id': 24,
    },
    {
        'name': 'Роснефть',
        'description': 'Раздел Нефть и газ',
        'research_section_id': 4,
        'source_id': 25,
    },
    {
        'name': 'Каменьщик',
        'description': 'Раздел Металлургия',
        'research_section_id': 5,
        'source_id': 26,
    },
    {
        'name': 'Металлург',
        'description': 'Раздел Металлургия',
        'research_section_id': 5,
        'source_id': 27,
    },
]
