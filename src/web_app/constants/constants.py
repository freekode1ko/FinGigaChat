#
# @dataclasses.dataclass
# class Rates:
#     """Отношение одной валюты к другой"""
#     name: str
#     table: DeclarativeBase
#     search_field: Any
#     get_field: Any
#     section: str
#     print_name: Optional[str] = None
#     name_change_filed: str = '%день'
#
#     def __str__(self) -> str:
#         return self.name if self.print_name is None else self.print_name
#
#
# all_exchange_rates: list[Rates] = [
#     ### FX Spot ###
#     Rates(
#         name='CNH/RUB (MOEX)',
#         table=Exc,
#         search_field=Exc.name,
#         get_field=Exc.value,
#         section='FX Spot',
#     ),
#     Rates(
#         name='USD/RUB (межбанк)',
#         table=Exc,
#         search_field=Exc.name,
#         get_field=Exc.value,
#         section='FX Spot',
#     ),
#     Rates(
#         name='EUR/RUB (межбанк)',
#         table=Exc,
#         search_field=Exc.name,
#         get_field=Exc.value,
#         section='FX Spot',
#     ),
#     # ### FX ЦБ ###
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='USD/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='EUR/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # ### FX Прочее
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#     # Rates(
#     #     name='CNH/RUB',
#     #     table=Exc,
#     #     search_field=Exc.name,
#     #     get_field=Exc.value,
#     #     section='FX ЦБ',
#     # ),
#
#     ### Процентные ставки и инфляция ###
#     Rates(
#         name='CNH/RUB',
#         table=Exc,
#         search_field=Exc.name,
#         get_field=Exc.value,
#         section='Процентные ставки и инфляция',
#     ),
#
#
#
# ]

bonds_names = [
    {
        'name': 'Годовые',
        'name_db': 'Россия годовые'
    },
    {
        'name': '2-летние',
        'name_db': 'Россия 2-летние'
    },
    {
        'name': '3-летние',
        'name_db': 'Россия 3-летние'
    },
    {
        'name': '5-летние',
        'name_db': 'Россия 5-летние'
    },
    {
        'name': '7-летние',
        'name_db': 'Россия 7-летние'
    },
    {
        'name': '10-летние',
        'name_db': 'Россия 10-летние'
    },
]

commodity_pricing_names = [
    {
        'name': 'Нефть Brent $/бар',
        'name_db': 'Нефть Brent'
    },
    {
        'name': 'Нефть Urals $/бар',
        'name_db': 'Нефть Urals'
    },
    {
        'name': "Газ (TTF $/'000м3)",
        'name_db': 'Газ'
    },

]
metals_pricing_names = [
    {
        'name': 'Золото USD/t,oz',
        'name_db': 'Gold USD/t,oz'
    },
    {
        'name': 'Медь USD/Lbs',
        'name_db': 'Copper USD/Lbs'
    },
    {
        'name': 'Уголь USD/T',
        'name_db': 'Coal USD/T'
    },
]
