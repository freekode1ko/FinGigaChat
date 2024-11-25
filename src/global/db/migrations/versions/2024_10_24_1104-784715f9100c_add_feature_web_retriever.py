"""add_feature_web_retriever

Revision ID: 784715f9100c
Revises: 553511343eb7
Create Date: 2024-10-24 11:04:25.978808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from models.models import Feature
from migrations.data.add_feature_web_retriever.data import BOT_FEATURES_DATA_WEB_RETRIEVER

# revision identifiers, used by Alembic.
revision: str = '784715f9100c'
down_revision: Union[str, None] = '553511343eb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def add_features(
        session: sa.orm.Session,
        data: dict[str, str],
):
    """
    Создание, сохранение объектов.
    :param session: Сессия бд.
    :param data:    Данные для создания экземпляров модели.
    """
    objs = [Feature(name=name, description=desc) for name, desc in data.items()]
    session.add_all(objs)
    session.commit()


def delete_features(
        session: sa.orm.Session,
        data: dict[str, str],
):
    """
    Удаление объектов.
    :param session: Сессия бд.
    :param data:    Данные для удаления экземпляров модели.
    """
    session.execute(sa.delete(Feature).where(Feature.name.in_(data.keys())))
    session.commit()


def upgrade() -> None:
    conn = op.get_bind()
    session = sa.orm.Session(bind=conn)
    add_features(session, BOT_FEATURES_DATA_WEB_RETRIEVER)


def downgrade() -> None:
    conn = op.get_bind()
    session = sa.orm.Session(bind=conn)
    delete_features(session, BOT_FEATURES_DATA_WEB_RETRIEVER)
