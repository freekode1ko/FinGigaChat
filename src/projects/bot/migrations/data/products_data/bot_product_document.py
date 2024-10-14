import os
from pathlib import Path

import sqlalchemy as sa

from configs import config
from migrations.models.products_data import new_models as models
from migrations.data.products_data import bot_product
from migrations.data.products_data import bot_product_group


PRODUCTS_DATA_ROOT_ABS_PATH = config.PATH_TO_SOURCES / 'products' / 'product_shelf'
HOT_OFFERS_DATA_ROOT_ABS_PATH = config.PATH_TO_SOURCES / 'products' / 'hot_offers'
PRODUCTS_DATA_PATH = Path('sources') / 'products' / 'product_shelf'
HOT_OFFERS_DATA_PATH = Path('sources') / 'products' / 'hot_offers'

HOT_OFFERS_DATA = [
    {
        'name': bot_product.data[0]['name'],
        'pdf_path': HOT_OFFERS_DATA_ROOT_ABS_PATH / 'Crediting',
    },
    {
        'name': bot_product.data[1]['name'],
        'pdf_path': HOT_OFFERS_DATA_ROOT_ABS_PATH / 'liabilities',
    },
    {
        'name': bot_product.data[2]['name'],
        'pdf_path': HOT_OFFERS_DATA_ROOT_ABS_PATH / 'GM_products',
    },
    {
        'name': bot_product.data[3]['name'],
        'pdf_path': HOT_OFFERS_DATA_ROOT_ABS_PATH / 'foreign_trade_activities',
    },
    {
        'name': bot_product.data[4]['name'],
        'pdf_path': HOT_OFFERS_DATA_ROOT_ABS_PATH / 'ecosystem',
    },
    {
        'name': bot_product.data[5]['name'],
        'pdf_path': HOT_OFFERS_DATA_ROOT_ABS_PATH / 'accumulated_coupon_income',
    },
]

PRODUCT_SHELF_DATA = [
    {
        'name': bot_product.data[6]['name'],
        'pdf_path': PRODUCTS_DATA_ROOT_ABS_PATH / 'Crediting',
    },
    {
        'name': bot_product.data[7]['name'],
        'pdf_path': PRODUCTS_DATA_ROOT_ABS_PATH / 'liabilities',
    },
    {
        'name': bot_product.data[8]['name'],
        'pdf_path': PRODUCTS_DATA_ROOT_ABS_PATH / 'GM_products',
    },
    {
        'name': bot_product.data[9]['name'],
        'pdf_path': PRODUCTS_DATA_ROOT_ABS_PATH / 'foreign_trade_activities',
    },
    {
        'name': bot_product.data[10]['name'],
        'pdf_path': PRODUCTS_DATA_ROOT_ABS_PATH / 'ecosystem',
    },
    {
        'name': bot_product.data[11]['name'],
        'pdf_path': PRODUCTS_DATA_ROOT_ABS_PATH / 'accumulated_coupon_income',
    },
]


data = []

# по имени продукта добавляем все файлы, если файлов нет, то пустую запись
# (отправка просто текста только для hot offers)
for product in HOT_OFFERS_DATA:
    select_product_id = sa.select(models.Product.id).where(
        models.Product.name == product['name'],
        models.Product.group_id == sa.select(
            models.ProductGroup.id
        ).where(
            models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).scalar_subquery(),
    ).limit(1)

    files = ([HOT_OFFERS_DATA_PATH / product['pdf_path'].stem / i for i in os.listdir(product['pdf_path'])]
             if product['pdf_path'].exists() else [])
    if files:
        for f in files:
            data.append({
                'product_id': select_product_id,
                'file_path': str(f),
                'description': '',
                'name': '',
            })
    else:
        data.append({
            'product_id': select_product_id,
            'file_path': '',
            'description': '',
            'name': '',
        })

# по имени продукта добавляем все файлы
for product in PRODUCT_SHELF_DATA:
    select_product_id = sa.select(models.Product.id).where(
        models.Product.name == product['name'],
        models.Product.group_id == sa.select(
            models.ProductGroup.id
        ).where(
            models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).scalar_subquery(),
    ).limit(1)

    files = ([PRODUCTS_DATA_PATH / product['pdf_path'].stem / i for i in os.listdir(product['pdf_path'])]
             if product['pdf_path'].exists() else [])
    for f in files:
        data.append({
            'product_id': select_product_id,
            'file_path': str(f),
            'description': '',
            'name': '',
        })
