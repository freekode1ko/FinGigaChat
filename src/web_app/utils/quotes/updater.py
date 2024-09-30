import asyncio
import datetime
import xml.etree.ElementTree as ET

import sqlalchemy as sa
from aiohttp import ClientSession
from sqlalchemy.dialects.postgresql import insert as insert_pg

from db import models
from db.database import async_session


async def update_cbr_quote(quote: models.Quotes):
    async with async_session() as session:
        url = 'https://www.cbr.ru/scripts/XML_dynamic.asp'  # FIXME to const
        async with ClientSession() as req_session:
            req = await req_session.get(
                url=url,
                params={
                    'date_req1': (datetime.date.today() - datetime.timedelta(days=365)).strftime('%d/%m/%Y'),
                    'date_req2': datetime.date.today().strftime('%d/%m/%Y'),
                    'VAL_NM_RQ': quote.params.get('CBR_ID'),
                },
                ssl=False,
                timeout=10
            )
            quotes_data_xml = await req.text()
        for quote_date in ET.fromstring(quotes_data_xml).findall('Record'):
            insert_stmt = insert_pg(models.QuotesValues).values(
                quote_id=quote.id,
                date=datetime.datetime.strptime(quote_date.attrib['Date'], "%d.%m.%Y").date(),
                value=float(quote_date.find('Value').text.replace(',', '.')),
            )
            upsert_stmt = insert_stmt.on_conflict_do_update(
                constraint='uq_quote_and_date',
                set_={
                    # 'quote_id': quote.id,
                    'date': datetime.datetime.strptime(quote_date.attrib['Date'], "%d.%m.%Y").date(),
                    'value': float(quote_date.find('Value').text.replace(',', '.')),
                }
            )
            await session.execute(upsert_stmt)
        await session.commit()


async def update_all_cbr():
    """Обновить все котировки с CBR асинхронно"""

    async with async_session() as session:
        stmt = await session.execute(sa.select(models.Quotes))
        quotes = stmt.scalars().fetchall()

        await asyncio.gather(*[update_cbr_quote(quote) for quote in quotes])
