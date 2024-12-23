"""add_relation_users_products

Revision ID: 93a8990e8897
Revises: f6c7ae1fa4aa
Create Date: 2024-12-22 20:28:04.239071

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '93a8990e8897'
down_revision: Union[str, None] = 'f6c7ae1fa4aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'relation_registered_user_products',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['bot_product.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['registered_user.user_id'], ),
        sa.PrimaryKeyConstraint('user_id', 'product_id'),
        comment='Таблица отношений между пользователями и продуктами для рассылки'
    )
    op.add_column(
        'bot_product',
        sa.Column(
            'is_new',
            sa.Boolean(),
            nullable=True,
            comment='Новый ли продукт, отвечает за отправку продуктов пользователям'
        )
    )
    op.add_column(
        'bot_product',
        sa.Column(
            'broadcast_message',
            sa.Text(),
            nullable=True,
            comment='Текст рассылки для продукта'
        )
    )


def downgrade() -> None:
    op.drop_column('bot_product', 'is_new')
    op.drop_column('bot_product', 'broadcast_message')
    op.drop_table('relation_registered_user_products')
