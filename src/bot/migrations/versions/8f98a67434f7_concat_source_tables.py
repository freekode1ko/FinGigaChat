"""Concat research_source and quote_source tables

Revision ID: 8f98a67434f7
Revises: 9caf77c81d11
Create Date: 2024-03-13 15:42:27.750020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f98a67434f7'
down_revision: Union[str, None] = '865943b6e583'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def add_source_groups(source_grp_table) -> None:
    groups = [
        {
            'id': 1,
            'name': 'Облигации',
            'name_latin': 'bonds',
        },
        {
            'id': 2,
            'name': 'Экономика',
            'name_latin': 'eco',
        },
        {
            'id': 3,
            'name': 'Курсы валют',
            'name_latin': 'exc',
        },
        {
            'id': 4,
            'name': 'Металлы',
            'name_latin': 'metals',
        },
        {
            'id': 5,
            'name': 'GigaParsers',
            'name_latin': 'GigaParsers',
        },
        {
            'id': 6,
            'name': 'Weekly Pulse',
            'name_latin': 'Weekly Pulse',
        },
        {
            'id': 7,
            'name': 'CIB',
            'name_latin': 'CIB',
        },
        {
            'id': 8,
            'name': 'Полианалист',
            'name_latin': 'Polyanalist',
        },
    ]
    op.bulk_insert(source_grp_table, groups)


def add_sources(source_table) -> None:
    sources = [
        {
            'name': 'ключевая ставка Банка России',
            'alt_names': [],
            'response_format': '[X%] - текущая ключевая ставка Банка России',
            'source': 'https://www.cbr.ru/hd_base/KeyRate',
            'source_group_id': 2,
        },
        {
            'name': 'текущая ставка RUONIA',
            'alt_names': [],
            'response_format': '[X%] - текущая ставка RUONIA',
            'source': 'https://www.cbr.ru/hd_base/ruonia',
            'source_group_id': 2,
        },
        {
            'name': 'LPR Китай',
            'alt_names': [],
            'response_format': '[X%] - LPR Китай',
            'source': 'https://tradingeconomics.com/china/interest-rate',
            'source_group_id': 2,
        },
        {
            'name': 'Ключевые ставки ЦБ',
            'alt_names': [],
            'response_format': 'Ключевые ставки ЦБ мира | Страна | Ставка | Предыдущая',
            'source': 'https://tradingeconomics.com/country-list/interest-rate',
            'source_group_id': 2,
        },
        {
            'name': 'Инфляция в России',
            'alt_names': [],
            'response_format': 'Инфляция в России | Дата | Инфляция, % г/г',
            'source': 'https://www.cbr.ru/hd_base/infl',
            'source_group_id': 2,
        },
        {
            'name': 'Облигации',
            'alt_names': [],
            'response_format': 'Лет до погашения  |  Доходность',
            'source': 'https://ru.investing.com/rates-bonds/world-government-bonds',
            'source_group_id': 1,
        },
        {
            'name': 'Медь',
            'alt_names': [],
            'response_format': 'Медь | X | X% | X% | X% | X%',
            'source': 'https://www.bloomberg.com/quote/LMCADS03:COM',
            'source_group_id': 4,
        },
        {
            'name': 'Алюминий',
            'alt_names': [],
            'response_format': 'Алюминий',
            'source': 'https://tradingeconomics.com/commodities',
            'source_group_id': 4,
        },
        {
            'name': 'ЖРС (Китай)',
            'alt_names': [],
            'response_format': 'ЖРС (Китай)',
            'source': 'https://investing.com/commodities/coal-(api2)-cif-ara-futures-historical-data',
            'source_group_id': 4,
        },
        {
            'name': 'Кокс. уголь (Au)',
            'alt_names': [],
            'response_format': 'Кокс. уголь (Au)',
            'source': 'https://www.barchart.com/futures/quotes/U7*0',
            'source_group_id': 4,
        },
        {
            'name': 'USD/RUB',
            'alt_names': [],
            'response_format': 'USD/RUB | [X]',
            'source': 'https://investing.com/currencies/usd-rub',
            'source_group_id': 3,
        },
        {
            'name': 'EUR/RUB',
            'alt_names': [],
            'response_format': 'EUR/RUB | [X]',
            'source': 'https://investing.com/currencies/eur-rub',
            'source_group_id': 3,
        },
        {
            'name': 'CNH/RUB',
            'alt_names': [],
            'response_format': 'CNH/RUB | [X]',
            'source': 'https://investing.com/currencies/cny-rub',
            'source_group_id': 3,
        },
        {
            'name': 'EUR/USD',
            'alt_names': [],
            'response_format': 'EUR/USD | [X]',
            'source': 'https://investing.com/currencies/eur-usd',
            'source_group_id': 3,
        },
        {
            'name': 'USD/CNH',
            'alt_names': [],
            'response_format': 'USD/CNH | [X]',
            'source': 'https://investing.com/currencies/usd-cnh',
            'source_group_id': 3,
        },
        {
            'name': 'Индекс DXY',
            'alt_names': [],
            'response_format': 'Индекс DXY | [X]',
            'source': 'https://investing.com/indices/usdollar',
            'source_group_id': 3,
        },
        {
            'name': 'Weekly Pulse',
            'alt_names': [],
            'response_format': 'Презентация Weekly Pulse с CIB Research',
            'source': 'https://research.sberbank-cib.com/group/guest/money',
            'source_group_id': 6,
        },
        {
            'name': 'Полианалист',
            'alt_names': [],
            'response_format': 'Полианалист',
            'source': 'ai-helper@mail.ru',
            'source_group_id': 8,
        },
    ]
    op.bulk_insert(source_table, sources)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    source_group_table = op.create_table('source_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('name_latin', postgresql.ARRAY(sa.Text()), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    comment='Справочник выделенных подгрупп среди источников'
    )
    parser_source_table = op.create_table('parser_source',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('alt_names', postgresql.ARRAY(sa.Text()), nullable=False),
    sa.Column('response_format', sa.Text(), nullable=True),
    sa.Column('source', sa.Text(), nullable=False),
    sa.Column('source_group_id', sa.Integer(), nullable=False),
    sa.Column('last_update_datetime', sa.DateTime(), nullable=True),
    sa.Column('previous_update_datetime', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['source_group_id'], ['source_group.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    comment='Справочник источников'
    )
    op.drop_table('quote_source')
    op.drop_table('quote_group')
    op.drop_table('research_source')
    # ### end Alembic commands ###
    add_source_groups(source_group_table)
    add_sources(parser_source_table)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('research_source',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('response_format', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('source', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('last_update_datetime', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.Column('previous_update_datetime', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='research_source_pkey')
    )
    op.create_table('quote_source',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('alias', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('block', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('response_format', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('source', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('last_update_datetime', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('quote_group_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('previous_update_datetime', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['quote_group_id'], ['quote_group.id'], name='quote_group_id', onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='quote_source_pkey'),
    comment='Справочник источников котировок'
    )
    op.create_table('quote_group',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='quote_group_pkey'),
    comment='Справочник выделенных среди котировок подгрупп'
    )
    op.drop_table('parser_source')
    op.drop_table('source_group')
    # ### end Alembic commands ###
