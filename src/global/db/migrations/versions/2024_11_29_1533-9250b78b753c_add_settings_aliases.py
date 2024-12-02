"""add settings_aliases

Revision ID: 9250b78b753c
Revises: 9982181d8fe8
Create Date: 2024-11-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9250b78b753c'
down_revision: Union[str, None] = '9982181d8fe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'settings_aliases',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('key', sa.String(length=255), unique=True, nullable=False, comment='Наименование константы'),
        sa.Column('name', sa.String(length=255), nullable=False, comment='Человекочитаемое наименование константы'),
        comment='Таблица с человекочитаемыми наименованиями констант из Redis',
    )


def downgrade():
    op.drop_table('settings_aliases')
