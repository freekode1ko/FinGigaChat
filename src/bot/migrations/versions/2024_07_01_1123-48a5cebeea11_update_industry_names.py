"""Update industry names

Revision ID: 48a5cebeea11
Revises: 8faf87b5512c
Create Date: 2024-07-01 11:23:13.839371

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '48a5cebeea11'
down_revision: Union[str, None] = '8faf87b5512c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    industry = sa.table('industry', sa.column('name', sa.String()))
    op.execute(
        sa.update(industry)
        .where(industry.c.name == 'нефтегаз')
        .values(name='Нефть и газ')
    )
    op.execute(
        sa.update(industry)
        .where(industry.c.name == 'финансовые институты')
        .values(name='финансовый сектор')
    )


def downgrade() -> None:
    industry = sa.table('industry', sa.column('name', sa.String()))

    op.execute(
        sa.update(industry)
        .where(industry.c.name == 'Нефть и газ')
        .values(name='нефтегаз')
    )
    op.execute(
        sa.update(industry)
        .where(industry.c.name == 'финансовый сектор')
        .values(name='финансовые институты')
    )
