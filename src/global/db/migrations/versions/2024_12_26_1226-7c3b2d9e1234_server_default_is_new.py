"""set server default for is_new in product_document

Revision ID: 7c3b2d9e1234
Revises: 5f549e4ab5c8
Create Date: 2024-12-26 11:10:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7c3b2d9e1234'
down_revision: Union[str, None] = '5f549e4ab5c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'bot_product_document',
        'is_new',
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=sa.text('false'),
        comment='Новый ли файл, отвечает за отправку пользователям'
    )


def downgrade() -> None:
    op.alter_column(
        'bot_product_document',
        'is_new',
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
        comment='Новый ли файл, отвечает за отправку пользователям'
    )
