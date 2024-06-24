"""Products data"""
import sqlalchemy as sa

from configs import config
from migrations.data.product_hierarchical_structure import bot_product_group
from migrations.models.product_hierarchical_structure import old_models, new_models

root_data = new_models.Product(
    id=0,
    parent_id=None,
    name='Продуктовая полка',
    name_latin='root',
    description='Актуальные предложения для клиента',
)

state_support = dict(
    parent_id=0,
    name='Господдержка',
    name_latin='state_support',
    description='Господдержка',
    display_order=3,
)


STATE_SUPPORT_SOURCES = config.PATH_TO_SOURCES / 'products' / 'state_support'


old_products = [
    # ------------- HOT OFFERS -----------------------
    {
        'name': 'Кредитование',
        'name_latin': bot_product_group.data[0]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'Пассивы',
        'name_latin': bot_product_group.data[0]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'GM',
        'name_latin': bot_product_group.data[0]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'ВЭД',
        'name_latin': bot_product_group.data[0]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'Экосистема',
        'name_latin': bot_product_group.data[0]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'Прочий НКД',
        'name_latin': bot_product_group.data[0]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[0]['name_latin'],
        ).limit(1),
    },

    # ------------- PRODUCT SHELF -----------------------
    {
        'name': 'Кредитование',
        'name_latin': bot_product_group.data[1]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'Пассивы',
        'name_latin': bot_product_group.data[1]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'GM',
        'name_latin': bot_product_group.data[1]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'ВЭД',
        'name_latin': bot_product_group.data[1]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'Экосистема',
        'name_latin': bot_product_group.data[1]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
    },
    {
        'name': 'Прочий НКД',
        'name_latin': bot_product_group.data[1]['name_latin'],
        'group_id': sa.select(old_models.ProductGroup.id).where(
            old_models.ProductGroup.name_latin == bot_product_group.data[1]['name_latin'],
        ).limit(1),
    },
]
