"""add CommodityResearch

Revision ID: 8e72b159ccbf
Revises: b07ad8c75ba6
Create Date: 2024-08-05 15:48:31.370452

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8e72b159ccbf'
down_revision: Union[str, None] = 'b07ad8c75ba6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'commodity_research',
        sa.Column(
            'id',
            sa.Integer,
            primary_key=True
        ),
        sa.Column(
            'commodity_id',
            sa.Integer,
            sa.ForeignKey('commodity.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
            unique=True
        ),
        sa.Column('title', sa.Text, nullable=True),
        sa.Column('text', sa.Text, nullable=False),
        sa.Column('file_name', sa.Text, nullable=True, unique=True),
    )


def downgrade() -> None:
    op.drop_table('commodity_research')
