"""Products data"""
from configs import config
from migrations.data.product_hierarchical_structure import new_models


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
