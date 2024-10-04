"""Загрузка котировок в БД"""
import asyncio
import datetime
import json
import xml.etree.ElementTree as ET
from collections import namedtuple

from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPNoContent
from sqlalchemy.dialects.postgresql import insert as insert_pg

from constants.constants import cbr_metals_parsing_list, moex_boards_names_order_list, moex_names_parsing_list, \
    yahoo_names_parsing_dict
from db import crud, models
from db.database import async_session
from log.logger_base import logger


async def load_cbr_quotes() -> None:
    """Загрузить котировки с cbr.ru"""
    logger.info('Начата загрузка котировок с cbr')

    async with ClientSession() as req_session:
        url = 'https://www.cbr.ru/scripts/XML_valFull.asp'
        req = await req_session.get(url=url, ssl=False, timeout=10)
        quotes_xml = await req.text()
        if req.status != 200:
            raise HTTPNoContent

    async with async_session() as session:
        last_update = datetime.date.today()
        update_func = 'update_cbr_quote'

        section_name = 'Котировки (ЦБ)'
        section_params = {
            '_value': 'get_quote_last',
            '%день': 'get_quote_day_day_param',
        }
        section = await crud.get_or_load_quote_section_by_name(session, section_name, section_params)

        quotes_list_in_xml = ET.fromstring(quotes_xml).findall('Item')
        try:
            for quote in quotes_list_in_xml:
                values = {
                    'name': quote.find('Name').text,
                    'params': {
                        'CBR_ID': quote.attrib['ID'].strip(),
                        'CBR_EngName': value.strip() if (value := quote.find('EngName').text) is not None else None,
                        'CBR_Nominal': int(value) if (value := quote.find('Nominal').text) is not None else None,
                        'CBR_ParentCode': value.strip() if (value := quote.find('ParentCode').text) is not None else None,
                        'CBR_ISO_Num_Code': int(value) if (value := quote.find('ISO_Num_Code').text) is not None else None,
                    },
                    'source': 'https://www.cbr.ru/scripts/XML_dynamic.asp',
                    'ticker': value.strip() if (value := quote.find('ISO_Char_Code').text) is not None else None,
                    'quotes_section_id': section.id,
                    'last_update': last_update,
                    'update_func': update_func,
                }
                await crud.custom_insert_or_update_to_postgres(
                    session,
                    model=models.Quotes,
                    values=values,
                    constraint='uq_quote_name_and_section',
                )
        except Exception as e:
            logger.error(f'Во время загрузки котировок по cbr произошла ошибка: {e}')
    logger.info('Закончена загрузка котировок с cbr')

async def load_cbr_metals() -> None:
    """Загрузка металлов с cbr.ru"""
    logger.info('Начата загрузка металлов с cbr')
    async with async_session() as session:
        last_update = datetime.date.today()
        update_func = 'update_cbr_metals'
        section_name = 'Металлы (ЦБ)'
        section_params = {
            '_value': 'get_quote_last',
            '%день': 'get_quote_day_day_param',
        }

        section = await crud.get_or_load_quote_section_by_name(session, section_name, section_params)

        try:
            for quote in cbr_metals_parsing_list:
                values = {
                    'name': quote['name'],
                    'params': {
                        'CBR_ID': quote['CBR_ID'],
                    },
                    'source': 'https://www.cbr.ru/scripts/xml_metall.asp',
                    'ticker': quote['ticker'],
                    'quotes_section_id': section.id,
                    'last_update': last_update,
                    'update_func': update_func,
                }

                await crud.custom_insert_or_update_to_postgres(
                    session,
                    model=models.Quotes,
                    values=values,
                    constraint='uq_quote_name_and_section',
                )
        except Exception as e:
            logger.error(f'Во время загрузки металлов с cbr произошла ошибка: {e}')
    logger.info('Закончена загрузка металлов с cbr')

async def load_moex_quotes():
    """Загрузить котировки с MOEX"""
    logger.info('Начата загрузка котировок с moex')

    async with ClientSession() as req_session:
        url = 'https://iss.moex.com/iss/engines/stock/markets/shares/securities.json'
        req = await req_session.get(url=url, ssl=False, timeout=10)
        quotes_name_json = await req.text()
        if req.status != 200:
            raise HTTPNoContent
        quotes_json = json.loads(quotes_name_json)

    async with async_session() as session:
        section_name = 'Котировки (MOEX)'  # FIXME TO CONST
        last_update = datetime.date.today()
        update_func = 'update_moex_quote'
        section_params = {
            '_value': 'get_quote_last',
            '%день': 'get_quote_day_day_param',
        }
        section = await crud.get_or_load_quote_section_by_name(session, section_name, section_params)

        MOEXData = namedtuple('MOEXData', quotes_json['securities']['columns'])

        quotes_list_from_json = [MOEXData(*x) for x in quotes_json['securities']['data']]
        try:
            for quote_name in moex_names_parsing_list:
                quotes_from_json_with_same_name = [_ for _ in quotes_list_from_json if _.SECID == quote_name]
                if not quotes_from_json_with_same_name:
                    logger.error(f'Не получилось загрузить котировку "{quote_name}" с MOEX')
                    continue

                for board_name in moex_boards_names_order_list:
                    try:
                        quote = next(filter(lambda x: x.BOARDID == board_name, quotes_from_json_with_same_name))
                        break
                    except StopIteration:
                        continue
                else:
                    quote = quotes_from_json_with_same_name[0]

                values = {
                    'name': quote.SHORTNAME,
                    'params': {
                        'MOEX_ID': quote.SECID,
                        'MOEX_EngName': quote.LATNAME,
                        'MOEX_FullName': quote.SECNAME,
                        'MOEX_MARKETCODE': quote.MARKETCODE
                    },
                    'source': f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{quote.SECID}/candles.json',
                    'ticker': quote.SECID,
                    'quotes_section_id': section.id,
                    'last_update': last_update,
                    'update_func': update_func,
                }

                await crud.custom_insert_or_update_to_postgres(
                    session,
                    model=models.Quotes,
                    values=values,
                    constraint='uq_quote_name_and_section',
                )
        except Exception as e:
            logger.error(f'Во время загрузки с moex произошла ошибка: {e}')
    logger.info('Закончена загрузка котировок с moex')

async def _load_yahoo_quote(section: models.QuotesSections, quote_name: str):
    """Загрузка одной котировки с yahoo"""
    last_update = datetime.date.today()
    update_func = 'update_yahoo_quote'
    logger.info(f'Начата загрузки данных котировки {quote_name} c yahoo началась')
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
            logger.error(f'Во время загрузки котировки {quote_name} c yahoo не получилось запросить страницу (HTTPNoContent)')
            return
    logger.info(f'Закончилась загрузки данных котировки {quote_name} c yahoo началась')

    try:
        async with async_session() as session:
            quote_meta_info = quote_data['chart']['result'][0]['meta']
            name = quote_meta_info['shortName']
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
            values = []
            for timestamp, low, high, open, close, volume in zip(  # noqa:A001
                    quote_data['chart']['result'][0]['timestamp'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['low'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['high'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['open'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['close'],
                    quote_data['chart']['result'][0]['indicators']['quote'][0]['volume'],
            ):
                values.append({
                    'quote_id': quote_id,
                    'date': datetime.datetime.fromtimestamp(timestamp),
                    'open': open,
                    'close': close,
                    'high': high,
                    'low': low,
                    'value': close,
                    'volume': volume,
                })

            await crud.custom_insert_or_update_to_postgres(
                session,
                model=models.QuotesValues,
                values=values,
                constraint='uq_quote_and_date',
            )
    except Exception as e:
        logger.error(f'Во время загрузки котировки {ticker} c yahoo произошла ошибка: {e}')
    logger.info(f'Загрузка котировки {ticker} c yahoo произошла успешно')

async def load_yahoo_quotes():
    """Загрузить котировок с Yahoo"""
    logger.info('Начата загрузка котировок с yahoo')
    section_params = {
        '_value': 'get_quote_last',
        '%день': 'get_quote_day_day_param',
    }
    batch = 5
    try:
        async with async_session() as session:
            for section_name, yahoo_sections_quotes in yahoo_names_parsing_dict.items():
                logger.info(f'Начата загрузка котировок с секции yahoo: {section_name}')
                section = await crud.get_or_load_quote_section_by_name(session, section_name, section_params)

                for i in range(0, len(yahoo_sections_quotes), batch):
                    await asyncio.gather(*[_load_yahoo_quote(section, quote_name) for quote_name in yahoo_sections_quotes[i:i + batch]])
                # await asyncio.gather(*[_load_yahoo_quote(section, quote_name) for quote_name in yahoo_sections_quotes])
                logger.info(f'Закончена загрузка котировок с секции yahoo: {section_name}')
    except Exception as e:
        logger.error(f'Во время загрузки с yahoo произошла ошибка: {e}')
    logger.info('Закончена загрузка котировок с yahoo')
