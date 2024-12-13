"""add broadcast & file tables

Revision ID: f6c7ae1fa4aa
Revises: 9982181d8fe8
Create Date: 2024-12-11 14:00:25.743256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from models.enums import FileType


# revision identifiers, used by Alembic.
revision: str = 'f6c7ae1fa4aa'
down_revision: Union[str, None] = '9982181d8fe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    file_type_enum = postgresql.ENUM(FileType, name='file_type', create_type=False)
    file_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'broadcast',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('message_type_id', sa.BigInteger(), sa.ForeignKey('message_type.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
        sa.Column('function_name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        comment='Рассылки сообщений в боте'
    )

    op.create_table(
        'telegram_message',
        sa.Column('telegram_message_id', sa.BigInteger(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('registered_user.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
        sa.Column('broadcast_id', sa.BigInteger(), sa.ForeignKey('broadcast.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False),
        sa.Column('send_datetime', sa.DateTime(timezone=True), nullable=False),
        comment='Доставленные пользователям сообщения'
    )

    op.create_table(
        'telegram_file',
        sa.Column('telegram_file_id', sa.String(length=255), primary_key=True),
        sa.Column('file_type', file_type_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        comment='Файлы бота в Telegram'
    )

    op.create_table(
        'broadcast_file',
        sa.Column('broadcast_id', sa.BigInteger(), sa.ForeignKey('broadcast.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
        sa.Column('telegram_file_id', sa.String(length=255), sa.ForeignKey('telegram_file.telegram_file_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
        comment='Связь между рассылками и файлами Telegram'
    )


def downgrade():
    op.drop_table('broadcast_file')
    op.drop_table('telegram_file')
    op.drop_table('telegram_message')
    op.drop_table('broadcast')
    file_type_enum = postgresql.ENUM(FileType, name='file_type', create_type=False)
    file_type_enum.drop(op.get_bind(), checkfirst=True)
