import datetime
import xml.etree.ElementTree as ET

import sqlalchemy as sa
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPNoContent
from sqlalchemy.dialects.postgresql import insert as insert_pg
from sqlalchemy.ext.asyncio import AsyncSession

from constants.constants import moex_parsing_list
from db import models
from db.database import async_session

# def parse_moex(json_data: dict[str, Any]) -> list[Quote]:
#     quotes = []
#     candles = json_data['candles']['data']
#     for candle in candles:
#         quote = Quote(
#             date=candle[0],  # Дата
#             open=candle[1],  # Открытие
#             high=candle[2],  # Максимум
#             low=candle[3],  # Минимум
#             close=candle[4],  # Закрытие
#             volume=candle[5]  # Объем
#         )
#         quotes.append(quote)
#     return quotes


async def load_cbr_quotes() -> None:
    """Загрузить котировки с cbr.ru"""
    async with async_session() as session:
        section_name = 'Котировки ЦБ'  # FIXME TO CONST
        last_update = datetime.date.today()
        update_func = 'update_cbr_quote'

        stmt = await session.execute(sa.select(models.QuotesSections).filter_by(name=section_name))
        section = stmt.scalar_one_or_none()
        if section is None:
            section = models.QuotesSections(
                name=section_name,
                params={
                    '_value': 'get_quote_now',
                    '%день': 'get_quote_day_day_param',
                }
            )
            session.add(
                section
            )
            await session.flush()

        async with ClientSession() as req_session:
            url = 'https://www.cbr.ru/scripts/XML_valFull.asp'  # FIXME TO CONST
            req = await req_session.get(url=url, ssl=False, timeout=10)
            quotes_xml = await req.text()
            if req.status != 200:
                return HTTPNoContent

            quotes_list_in_xml = ET.fromstring(quotes_xml).findall('Item')
            for quote in quotes_list_in_xml:
                name = quote.find('Name').text
                source = "https://www.cbr.ru/scripts/XML_dynamic.asp"
                params = {
                    'CBR_ID': quote.attrib['ID'].strip(),
                    'CBR_EngName': value.strip() if (value := quote.find('EngName').text) is not None else None,
                    'CBR_Nominal': int(value) if (value := quote.find('Nominal').text) is not None else None,
                    'CBR_ParentCode': value.strip() if (value := quote.find('ParentCode').text) is not None else None,
                    'CBR_ISO_Num_Code': int(value) if (value := quote.find('ISO_Num_Code').text) is not None else None,
                    'CBR_ISO_Char_Code': value.strip() if (value := quote.find('ISO_Char_Code').text) is not None else None,
                }
                insert_stmt = insert_pg(models.Quotes).values(
                    name=name,
                    params=params,
                    source=source,
                    quotes_section_id=section.id,
                    last_update=last_update,
                    update_func=update_func,
                )
                upsert_stmt = insert_stmt.on_conflict_do_update(
                    constraint='uq_quote_name_and_section',
                    set_={
                        'name': name,
                        'params': params,
                        'source': source,
                        'quotes_section_id': section.id,
                        'last_update': last_update,
                        'update_func': update_func,
                    }
                )

                await session.execute(upsert_stmt)
            await session.commit()

async def load_MOEX_quotes():
    pass
#     section_name = 'MOEX'  # FIXME TO CONST
#     last_update = datetime.date.today()
#     update_func = 'update_moex_quote'
#
#     async with async_session() as session:
#         for i in moex_parsing_list:
#
#             stmt = await session.execute(sa.select(models.QuotesSections).filter_by(name=section_name))
#             section = stmt.scalar_one_or_none()
#             if section is None:
#                 section = models.QuotesSections(
#                     name=section_name,
#                     params={
#                         '_value': 'get_quote_now',
#                         '%день': 'get_quote_day_day_param',
#                     }
#                 )
#                 session.add(
#                     section
#                 )
#                 await session.flush()
#
#         insert_stmt = insert_pg(models.QuotesValues).values(
#             quote_id=quote.id,
#             date=datetime.datetime.strptime(quote_date.attrib['Date'], "%d.%m.%Y").date(),
#             value=float(quote_date.find('Value').text.replace(',', '.')),
#         )
#         upsert_stmt = insert_stmt.on_conflict_do_update(
#             constraint='uq_quote_and_date',
#             set_={
#                 # 'quote_id': quote.id,
#                 'date': datetime.datetime.strptime(quote_date.attrib['Date'], "%d.%m.%Y").date(),
#                 'value': float(quote_date.find('Value').text.replace(',', '.')),
#             }
#         )


async def laod_all_sources():
    pass