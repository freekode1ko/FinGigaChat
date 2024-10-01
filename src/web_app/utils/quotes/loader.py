import datetime
import json
import xml.etree.ElementTree as ET
from collections import namedtuple

import sqlalchemy as sa
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPNoContent
from sqlalchemy.dialects.postgresql import insert as insert_pg

from constants.constants import moex_names_parsing_list, moex_boards_names_order_list
from db import models
from db.database import async_session


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
                    '_value': 'get_quote_last',
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


async def load_moex_quotes():
    """Загрузить котировки с MOEX"""

    async with async_session() as session:
        section_name = 'Котировки (MOEX)'  # FIXME TO CONST
        last_update = datetime.date.today()
        update_func = 'update_moex_quote'

        stmt = await session.execute(sa.select(models.QuotesSections).filter_by(name=section_name))
        section = stmt.scalar_one_or_none()
        if section is None:
            section = models.QuotesSections(
                name=section_name,
                params={
                    '_value': 'get_quote_last',
                    '%день': 'get_quote_day_day_param',
                }
            )
            session.add(
                section
            )
            await session.flush()

        async with ClientSession() as req_session:
            url = 'https://iss.moex.com/iss/engines/stock/markets/shares/securities.json'
            req = await req_session.get(url=url, ssl=False, timeout=10)
            quotes_name_json = await req.text()
            if req.status != 200:
                return HTTPNoContent

            quotes_json = json.loads(quotes_name_json)
            MOEXData = namedtuple('MOEXData', quotes_json['securities']['columns'])

            quotes_list_from_json = [MOEXData(*x) for x in quotes_json['securities']['data']]

            for quote_name in moex_names_parsing_list:
                quotes_from_json_with_same_name = [_ for _ in quotes_list_from_json if _.SECID == quote_name]

                for board_name in moex_boards_names_order_list:
                    try:
                        quote = next(filter(lambda x: x.BOARDID == board_name, quotes_from_json_with_same_name))
                    except StopIteration:
                        continue
                else:
                    quote = quotes_from_json_with_same_name[0]

                name = quote.SHORTNAME
                source = f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{quote.SECID}/candles.json'
                params = {
                    'MOEX_ID': quote.SECID,
                    'MOEX_EngName': quote.LATNAME,
                    'CBR_FullName': quote.SECNAME,
                    'CBR_MARKETCODE': quote.MARKETCODE
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
