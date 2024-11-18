"""quotes.id & quotes_values.id integer to biginteger change

Revision ID: 9982181d8fe8
Revises: b6ec26f13742
Create Date: 2024-11-15 14:33:45.792677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9982181d8fe8'
down_revision: Union[str, None] = 'b6ec26f13742'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint('fk_quotes_values_quote_id', 'quotes_values', type_='foreignkey')
    op.alter_column(
        'quotes',
        'id',
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.alter_column(
        'quotes_values',
        'id',
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.alter_column(
        'quotes_values',
        'quote_id',
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        'fk_quotes_values_quote_id',
        'quotes_values',
        'quotes',
        ['quote_id'],
        ['id']
    )


def downgrade():
    op.drop_constraint('fk_quotes_values_quote_id', 'quotes_values', type_='foreignkey')
    op.alter_column(
        'quotes',
        'id',
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        'quotes_values',
        'id',
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.alter_column(
        'quotes_values',
        'quote_id',
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=False,
    )
    op.create_foreign_key(
        'fk_quotes_values_quote_id',
        'quotes_values',
        'quotes',
        ['quote_id'],
        ['id']
    )
