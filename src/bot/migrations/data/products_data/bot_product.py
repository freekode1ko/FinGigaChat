import sqlalchemy as sa

from db import models
from migrations.data.products_data import bot_product_group

data = [
    # ------------- HOT OFFERS -----------------------
    {
        'name': 'Кредитование',
        'description': 'Актуальные предложения по продуктам кредитования',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
        'display_order': 1,
    },
    {
        'name': 'Пассивы',
        'description': 'Актуальные предложения по продуктам пассивов',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
        'display_order': 2,
    },
    {
        'name': 'GM',
        'description': 'Актуальные предложения по продуктам GM',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
        'display_order': 3,
    },
    {
        'name': 'ВЭД',
        'description': 'Актуальные предложения по продуктам ВЭД',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
        'display_order': 4,
    },
    {
        'name': 'Экосистема',
        'description': 'Актуальные предложения по продуктам экосистемы',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
        'display_order': 5,
    },
    {
        'name': 'Прочий НКД',
        'description': 'Актуальные предложения по прочим продуктам НКД',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
        'display_order': 6,
    },

    # ------------- PRODUCT SHELF -----------------------
    {
        'name': 'Кредитование',
        'description': 'Продукты кредитования',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
        'display_order': 1,
    },
    {
        'name': 'Пассивы',
        'description': 'Продукты пассивов',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
        'display_order': 2,
    },
    {
        'name': 'GM',
        'description': 'Продукты GM',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
        'display_order': 3,
    },
    {
        'name': 'ВЭД',
        'description': 'Продукты ВЭД',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
        'display_order': 4,
    },
    {
        'name': 'Экосистема',
        'description': 'Продукты экосистемы',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
        'display_order': 5,
    },
    {
        'name': 'Прочий НКД',
        'description': 'Прочие продукты НКД',
        'group_id': sa.select(models.ProductGroup.id).where(
            models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
        'display_order': 6,
    },
]
