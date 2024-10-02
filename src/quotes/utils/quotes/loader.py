import asyncio
import datetime
import json
import xml.etree.ElementTree as ET
from collections import namedtuple

import sqlalchemy as sa
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPNoContent
from sqlalchemy.dialects.postgresql import insert as insert_pg

from constants.constants import moex_names_parsing_list, moex_boards_names_order_list, yahoo_names_parsing_dict, \
    cbr_metals_parsing_list
from db import models
from db.database import async_session


async def load_cbr_quotes() -> None:
    """Загрузить котировки с cbr.ru"""
    async with async_session() as session:
        section_name = 'Котировки (ЦБ)'  # FIXME TO CONST
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
                }
                ticker = value.strip() if (value := quote.find('ISO_Char_Code').text) is not None else None
                insert_stmt = insert_pg(models.Quotes).values(
                    name=name,
                    params=params,
                    source=source,
                    ticker=ticker,
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
                        'ticker': ticker,
                        'quotes_section_id': section.id,
                        'last_update': last_update,
                        'update_func': update_func,
                    }
                )

                await session.execute(upsert_stmt)
            await session.commit()

async def load_cbr_metals() -> None:
    """Загрузка металлов с cbr.ru"""

    async with async_session() as session:
        section_name = 'Металлы (ЦБ)'  # FIXME TO CONST
        last_update = datetime.date.today()
        update_func = 'update_cbr_metals'

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
            url = 'https://www.cbr.ru/scripts/xml_metall.asp'  # FIXME TO CONST

            for quote in cbr_metals_parsing_list:
                name = quote['name']
                source = url
                params = {
                    'CBR_ID': quote['CBR_ID'],
                }
                ticker = quote['ticker']
                insert_stmt = insert_pg(models.Quotes).values(
                    name=name,
                    params=params,
                    source=source,
                    ticker=ticker,
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
                        'ticker': ticker,
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
                    'MOEX_FullName': quote.SECNAME,
                    'MOEX_MARKETCODE': quote.MARKETCODE
                }
                ticker = quote.SECID
                insert_stmt = insert_pg(models.Quotes).values(
                    name=name,
                    params=params,
                    source=source,
                    ticker=ticker,
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
                        'ticker': ticker,
                        'quotes_section_id': section.id,
                        'last_update': last_update,
                        'update_func': update_func,
                    }
                )
                await session.execute(upsert_stmt)
        await session.commit()


async def _load_yahoo_quote(section: models.QuotesSections, quote_name: str):
    last_update = datetime.date.today()
    update_func = 'update_yahoo_quote'

    async with ClientSession() as req_session:
        url = f'https://query1.finance.yahoo.com/v8/finance/chart/{quote_name}'
        req = await req_session.get(
            url=url,
            params={
                'range': '1y',
                'interval': '1d',
            },
            ssl=False,
            timeout=10
        )
        quote_data = json.loads(await req.text())
        if req.status != 200:
            return HTTPNoContent

    quote_meta_info = quote_data['chart']['result'][0]['meta']

    async with async_session() as session:
        try:
            name = quote_meta_info['shortName']
        except Exception as e:
            print(quote_meta_info)
            raise e
        source = url
        ticker = quote_name
        params = {
            'YAHOO_Currency': quote_meta_info['currency'],
        }

        insert_stmt = insert_pg(models.Quotes).values(
            name=name,
            params=params,
            source=source,
            ticker=ticker,
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
                'ticker': ticker,
                'quotes_section_id': section.id,
                'last_update': last_update,
                'update_func': update_func,
            }
        ).returning(models.Quotes.id)
        result = await session.execute(upsert_stmt)
        await session.commit()

        quote_id = result.scalar()
        try:
            for timestamp, low, high, open, close, volume in zip(
                    quote_data['chart']['result'][0]['timestamp'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['low'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['high'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['open'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['close'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['volume'],
            ):
                insert_stmt = insert_pg(models.QuotesValues).values(
                    quote_id=quote_id,
                    date=datetime.datetime.fromtimestamp(timestamp),  # FIXME
                    open=open,
                    close=close,
                    high=high,
                    low=low,
                    value=close,
                    volume=volume,
                )
                upsert_stmt = insert_stmt.on_conflict_do_update(
                    constraint='uq_quote_and_date',
                    set_={
                        'open': open,
                        'close': close,
                        'high': high,
                        'low': low,
                        'value': close,
                        'volume': volume,
                    }
                )
                await session.execute(upsert_stmt)

        except Exception as e:
            print(url)
        await session.commit()


async def load_yahoo_quotes():
    """Загрузить котировки с Yahoo"""

    async with async_session() as session:
        for section_name, yahoo_sections_quotes in yahoo_names_parsing_dict.items():
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
                await session.commit()

            await asyncio.gather(*[_load_yahoo_quote(section, quote_name) for quote_name in yahoo_sections_quotes])
