import datetime
import xml.etree.ElementTree as ET

import sqlalchemy as sa
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPNoContent
from sqlalchemy.dialects.postgresql import insert as insert_psql
from sqlalchemy.ext.asyncio import AsyncSession

from db import models
from db.database import async_session
from utils.quotes_update import update_all_CBR


async def update_quotes_params(quotes):
    pass


async def add_new_quotes(quotes):
    pass


async def load_CBR_quotes(session: AsyncSession) -> None:
    """Загрузить котировки с cbr.ru"""
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
            insert_stmt = insert_psql(models.Quotes).values(
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


async def update_quotes_data():
    """Обновляет данные о котировказ из конфига, перед запуском приложения"""
    async with async_session() as session:
        await load_CBR_quotes(session)
        print('#' * 100)
        print('#' * 100)
        print('#' * 100)
    await update_all_CBR()

    # existing_quotes = []
    # not_existing_quotes = []

    # Проверка, что уже есть в базе

    # quotes = await session.execute(sa.select(models.Quotes))
    # for i in session.scalars(quotes):
    #     if i in quotes_data:  # FIXME изменить in проверку
    #         existing_quotes.append(i)
    #     not_existing_quotes.append(i)

    # await update_quotes_params(existing_quotes)  # Обновить данные, если изменились
    # await add_new_quotes(not_existing_quotes)  # Добавить новые
