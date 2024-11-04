"""Обновление котировок"""
import asyncio
import datetime
import json
import xml.etree.ElementTree as ET
from collections import namedtuple

import sqlalchemy as sa
from aiohttp import ClientSession

from db import models
from db.crud import custom_insert_or_update_to_postgres
from db.database import async_session
from log.logger_base import logger


async def update_cbr_quote(quote: models.Quotes):
    """Обновление котировок с cbr"""
    async with async_session() as session:
        async with ClientSession() as req_session:
            req = await req_session.get(
                url=quote.source,
                params={
                    'date_req1': (datetime.date.today() - datetime.timedelta(days=365)).strftime('%d/%m/%Y'),
                    'date_req2': datetime.date.today().strftime('%d/%m/%Y'),
                    'VAL_NM_RQ': quote.params.get('CBR_ID'),
                },
                ssl=False,
                timeout=10
            )
            quotes_data_xml = await req.text()

        values = []
        for quote_date in ET.fromstring(quotes_data_xml).findall('Record'):
            values.append({
                'quote_id': quote.id,
                'date': datetime.datetime.strptime(quote_date.attrib['Date'], '%d.%m.%Y').date(),
                'value': float(quote_date.find('Value').text.replace(',', '.')),
            })
        await custom_insert_or_update_to_postgres(
            session=session,
            model=models.QuotesValues,
            values=values,
            constraint='uq_quote_and_date',
        )


async def update_all_cbr():
    """Обновить все котировки с cbr"""
    logger.info('Начато обновление котировок с cbr')
    try:
        async with async_session() as session:
            stmt = await session.execute(sa.select(models.QuotesSections).filter_by(name='Котировки (ЦБ)'))
            section = stmt.scalar_one_or_none()

            stmt = await session.execute(
                sa.select(models.Quotes).filter_by(quotes_section_id=section.id)
            )
            quotes = stmt.scalars().fetchall()

        await asyncio.gather(*[update_cbr_quote(quote) for quote in quotes])
    except Exception as e:
        logger.error(f'Во время обновления котировок по cbr произошла ошибка: {e}')
    logger.info('Закончено обновление котировок с cbr')


async def update_moex_quotes(quote: models.Quotes):
    """Обновление котировок с moex"""
    async with async_session() as session:
        async with ClientSession() as req_session:

            req = await req_session.get(
                url=quote.source,
                params={
                    'from': (datetime.date.today() - datetime.timedelta(days=365)).strftime('%Y-%m-%d'),
                    'till': datetime.date.today().strftime('%Y-%m-%d'),
                    'interval': 24,
                    'start': 0,
                },
                ssl=False,
                timeout=10
            )
            data = await req.text()
            try:
                quotes_data_json = json.loads(data)
            except Exception as e:
                print(req.url)
                print(data)
                raise e
            MOEXDataCandles = namedtuple('MOEXDataCandles', quotes_data_json['candles']['columns'])

            candles_list_from_json = [MOEXDataCandles(*x) for x in quotes_data_json['candles']['data']]

        values = []
        for quote_data in candles_list_from_json:
            values.append({
                'quote_id': quote.id,
                'date': datetime.datetime.strptime(quote_data.begin.split()[0], '%Y-%m-%d').date(),
                'open': quote_data.open,
                'close': quote_data.close,
                'high': quote_data.high,
                'low': quote_data.low,
                'value': quote_data.open,
                'volume': quote_data.volume,
            })

        await custom_insert_or_update_to_postgres(
            session=session,
            model=models.QuotesValues,
            values=values,
            constraint='uq_quote_and_date',
        )


async def update_all_moex():
    """Обновление всех котировок с moex"""
    logger.info('Начато обновление котировок с moex')
    try:
        async with async_session() as session:
            stmt = await session.execute(sa.select(models.QuotesSections).filter_by(name='Котировки (MOEX)'))
            section = stmt.scalar_one_or_none()

            stmt = await session.execute(
                sa.select(models.Quotes).filter_by(quotes_section_id=section.id)
            )
            quotes = stmt.scalars().fetchall()

        batch = 50
        for i in range(0, len(quotes), batch):
            await asyncio.gather(*[update_moex_quotes(quote) for quote in quotes[i:i + batch]])
    except Exception as e:
        logger.error(f'Во время обновление с moex произошла ошибка: {e}')
    logger.info('Закончено обновление котировок с moex')


async def update_cbr_metals():
    """Обновление всех котировок по металлам с cbr"""
    logger.info('Начато обновление металлов с cbr')
    try:
        async with ClientSession() as req_session:
            req = await req_session.get(
                url='https://www.cbr.ru/scripts/xml_metall.asp',
                params={
                    'date_req1': (datetime.date.today() - datetime.timedelta(days=365)).strftime('%d/%m/%Y'),
                    'date_req2': datetime.date.today().strftime('%d/%m/%Y'),
                },
                ssl=False,
                timeout=10
            )
            quotes_data_xml = await req.text()
            quote_data = ET.fromstring(quotes_data_xml)
        async with async_session() as session:
            stmt = await session.execute(sa.select(models.QuotesSections).filter_by(name='Металлы (ЦБ)'))
            section = stmt.scalar_one_or_none()

            stmt = await session.execute(
                sa.select(models.Quotes).filter_by(quotes_section_id=section.id)
            )
            quotes = stmt.scalars().fetchall()

            values = []
            for quote in quotes:
                for data in quote_data.findall('Record'):
                    if int(data.attrib['Code']) != quote.params['CBR_ID']:
                        continue

                    values.append({
                        'quote_id': quote.id,
                        'date': datetime.datetime.strptime(data.attrib['Date'], '%d.%m.%Y').date(),
                        'value': float(data.find('Buy').text.replace(',', '.')),
                    })

            await custom_insert_or_update_to_postgres(
                session=session,
                model=models.QuotesValues,
                values=values,
                constraint='uq_quote_and_date',
            )
    except Exception as e:
        logger.error(f'Во время обновления металлов с cbr произошла ошибка: {e}')
    logger.info('Закончено обновление металлов с cbr')
