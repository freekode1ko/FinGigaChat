"""Старые таблицы"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class ProductGroup(Base):
    __tablename__ = 'bot_product_group'
    __table_args__ = (
        sa.UniqueConstraint('name', name='group_name'),
        {'comment': 'Справочник групп продуктов (продуктовая полка, hot offers)'},
    )

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='id группы в базе')
    name = sa.Column(sa.String(255), nullable=False, comment='Имя группы')
    name_latin = sa.Column(sa.String(255), nullable=False, comment='Имя группы eng')
    description = sa.Column(sa.Text(), nullable=True, server_default=sa.text("''::text"),
                            comment='Описание группы (текст меню тг)')
    display_order = sa.Column(sa.Integer(), server_default=sa.text('0'), nullable=False, comment='Порядок отображения')


class Product(Base):
    __tablename__ = 'bot_product'
    __table_args__ = {'comment': 'Справочник продуктов (кредит, GM, ...)'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='id продукта в базе')
    name = sa.Column(sa.String(255), nullable=False, comment='Имя продукта (кредит, GM, ...)')
    description = sa.Column(sa.Text(), nullable=True, server_default=sa.text("''::text"),
                            comment='Текст сообщения, которое выдается при нажатии на продукт')
    display_order = sa.Column(sa.Integer(), server_default=sa.text('0'), nullable=False, comment='Порядок отображения')
    group_id = sa.Column(sa.ForeignKey('bot_product_group.id', ondelete='CASCADE', onupdate='CASCADE'),
                         primary_key=False, nullable=False, comment='id группы продукта')


class ProductDocument(Base):
    __tablename__ = 'bot_product_document'
    __table_args__ = {'comment': 'Справочник файлов продуктов'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='id файла в базе')
    file_path = sa.Column(sa.Text(), nullable=False, comment='Путь к файлу в системе')
    name = sa.Column(sa.String(255), nullable=False, comment='Наименование документа или продуктового предложения')
    description = sa.Column(sa.Text(), nullable=True, server_default=sa.text("''::text"), comment='Описание')
    product_id = sa.Column(sa.ForeignKey('bot_product.id', ondelete='CASCADE', onupdate='CASCADE'),
                           primary_key=False, nullable=False, comment='id категории продукта')
