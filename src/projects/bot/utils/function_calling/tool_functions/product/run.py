"""Тулза по продуктам"""

import sqlalchemy as sa
from fuzzywuzzy import process
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from db import models
from db.database import async_session
from handlers.products import callbacks
from handlers.products import get_group_products
from handlers.products.handler import main_menu
from utils.function_calling.tool_functions.product.utils import get_root_id
from utils.function_calling.tool_functions.utils import parse_runnable_config


@tool
async def get_product_list(name: str | None, runnable_config: RunnableConfig) -> str:
    """Возвращает пользователю список доступных предложений по названию продукта.

    Господдержка (Господдержка)
    Hot offers, (Hot offers)
    TARS (Продукты GM)
    Размещение долларовой ликвидности через сделки РЕПО, (Продукты GM)
    Заем бумаг для Н26 (Продукты GM)
    Ассиметричный коллар (Продукты GM)
    Кэпы с лимитом на количество платежей и лимитом на сумму выплат на год на 18.0% (Продукты GM)
    Процентное хеджирование (Продукты GM)
    Валютное хеджирование (Продукты GM)
    Синтетическое финансирование (Продукты GM)
    Platform V. (Актуальные предложения по продуктам экосистемы)
    Bi.Zone (Актуальные предложения по продуктам экосистемы)
    Современные Технологии(СовТех), (Современные Технологии СовТех )
    ЦРТ, (ЦРТ)
    СберУниверситет (Актуальные предложения по продуктам экосистемы)
    Экосистема (Актуальные предложения по продуктам экосистемы)
    Прочие продукты НКД (Актуальные предложения по прочим НКД)
    Кредитование (Актуальные предложения по продуктам кредитования)
    Пассивы (Актуальные предложения по продуктам пассивов)
    GM (Актуальные предложения по продуктам GM)
    Лизинг (Актуальные предложения по продуктам Лизинга)
    ВЭД (Актуальные предложения по продуктам ВЭД)
    Trade Finance (Продукты Департамента Торгового финансирования)
    Пассивы (Продукты пассивов)
    Кредитование (Продукты кредитования)
    GM (Продукты GM)
    ВЭД (Продукты ВЭД)
    Экосистема (Продукты экосистемы)
    Прочий НКД (Прочие продукты НКД)
    Trade Finance (Продукты Департамента Торгового финансирования)
    Эскроу (Эскроу)
    Международный бизнес (Международный бизнес)
    Аккредитивы (Аккредитив – это финансовый инструмент, который помогает обезопасить сделку между покупателем и продавцом.)
    Hot offers, (Hot offers)
    Аккредитивы по поручению ЮЛ (Аккредитив – это обязательство банка, выпущенное им по поручению клиента (покупателя ЮЛ))
    Аккредитивы по поручению ФЛ (Аккредитив – инструмент, который помогает обезопасить сделку между покупателем и продавцом.)
    Непокрытые (Акрредитв ЮЛ)
    Покрытые (Аккредитив ЮЛ)
    Voice2X (Voice2X: Голос управляет процессами)
    Системы упралвления качеством (Умные решения для контакт-центров)
    Нестор.Brief (Нестор.Brief)
    ЦРТ AI-Трансформация (ЦРТ AI-Трансформация)
    Продуктовая полка (Актуальные предложения для клиента)

    Args:
        name (str): название продуктов из списка и его описание в скобочках
    return:
        (str): Строка с доступными разделами.
    """
    runnable_config = parse_runnable_config(runnable_config)

    async with async_session() as session:
        stmt = sa.select(models.Product)
        result = await session.execute(stmt)
        products = [_ for _ in result.scalars()]

    matches = process.extractBests(name, [product.name for product in products], score_cutoff=95)
    if len(matches) >= 1:
        product = next(filter(lambda x: x.name == matches[0][0], products))

        if product.parent_id is None:
            await main_menu(runnable_config.message)
            return

        callback_data = callbacks.ProductsMenuData(
            menu=callbacks.ProductsMenusEnum.group_products,
            product_id=product.id,
            root_id=get_root_id(product, products)
        )
        await get_group_products(runnable_config.message, callback_data, next(filter(lambda x: x.name == matches[0][0], products)).id)
    else:
        raise Exception
