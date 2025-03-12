"""add cascade to users quotes subscriptions

Revision ID: 7c3b2d9e1235
Revises: 7c3b2d9e1234
Create Date: 2025-03-12 00:00:00

"""
from alembic import op


revision = '7c3b2d9e1235'
down_revision = '7c3b2d9e1234'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('users_quotes_subscriptions_user_id_fkey', 'users_quotes_subscriptions', type_='foreignkey')
    op.drop_constraint('users_quotes_subscriptions_quote_id_fkey', 'users_quotes_subscriptions', type_='foreignkey')
    op.create_foreign_key(
        'users_quotes_subscriptions_user_id_fkey', 'users_quotes_subscriptions', 'registered_user',
        ['user_id'], ['user_id'],
        onupdate='CASCADE', ondelete='CASCADE',
    )
    op.create_foreign_key(
        'users_quotes_subscriptions_quote_id_fkey', 'users_quotes_subscriptions', 'quotes',
        ['quote_id'], ['id'],
        onupdate='CASCADE', ondelete='CASCADE',
    )


def downgrade():
    op.drop_constraint('users_quotes_subscriptions_user_id_fkey', 'users_quotes_subscriptions', type_='foreignkey')
    op.drop_constraint('users_quotes_subscriptions_quote_id_fkey', 'users_quotes_subscriptions', type_='foreignkey')
    op.create_foreign_key(
        'users_quotes_subscriptions_user_id_fkey', 'users_quotes_subscriptions', 'registered_user',
        ['user_id'], ['user_id'],
    )
    op.create_foreign_key(
        'users_quotes_subscriptions_quote_id_fkey', 'users_quotes_subscriptions', 'quotes',
        ['quote_id'], ['id'],
    )
