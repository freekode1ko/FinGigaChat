"""Собираемые курсы валют"""

import sqlalchemy as sa

from db import models
from migrations.data.new_exchange_sources import exc_types, parser_source
from migrations.models.new_exchange_sources import new_models


data = []

for display_order, source in enumerate(parser_source.new_data):
    data.append({
        'name': source['name'],
        'display_order': display_order,
        'exc_type_id': (sa.select(new_models.ExcType.id)
                        .where(new_models.ExcType.name == exc_types.data[display_order // 3]['name'])
                        .scalar_subquery()),
        'parser_source_id': (sa.select(models.ParserSource.id)
                             .where(models.ParserSource.source == source['source'],
                                    models.ParserSource.name == source['name'])
                             .scalar_subquery()),
    })
