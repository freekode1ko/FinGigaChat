"""Products data"""

from migrations.data.product_hierarchical_structure import new_models


root_data = new_models.Product(
    id=0,
    parent_id=None,
    name='Продуктовая полка',
    name_latin='root',
    description='Актуальные предложения для клиента',
)

new_data = [
    new_models.Product(
        parent_id=0,
        name='Господдержка',
        name_latin='state_support',
        description='Господдержка',
        display_order=3,
    ),
]
