"""Новые таблицы"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base, relationship

from models.enums import FormatType

Base = declarative_base()


class Product(Base):
    __tablename__ = 'bot_product'
    __table_args__ = {'comment': 'Справочник продуктов (кредит, GM, ...)'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='id файла в базе')
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('bot_product.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=True)
    children = relationship('Product', back_populates='parent')
    parent = relationship('Product', back_populates='children', remote_side=[id])

    name = sa.Column(sa.String(255), nullable=False, comment='Имя продукта (кредит, GM, ...)')
    name_latin = sa.Column(sa.String(255), nullable=True, comment='Имя eng', server_default=sa.text(''))
    send_documents_format_type = sa.Column(sa.Integer(), server_default=sa.text(str(FormatType.group_files)),
                                        nullable=False, comment='Формат выдачи документов')
    description = sa.Column(sa.Text(), nullable=True, server_default=sa.text("''::text"),
                         comment='Текст сообщения, которое выдается при нажатии на продукт')
    display_order = sa.Column(sa.Integer(), server_default=sa.text('0'), nullable=False, comment='Порядок отображения')


class ProductDocument(Base):
    __tablename__ = 'bot_product_document'
    __table_args__ = {'comment': 'Справочник файлов продуктов'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='id файла в базе')
    file_path = sa.Column(sa.Text(), nullable=False, comment='Путь к файлу в системе')
    name = sa.Column(sa.String(255), nullable=False, comment='Наименование документа или продуктового предложения')
    description = sa.Column(sa.Text(), nullable=True, server_default=sa.text("''::text"), comment='Описание')
    product_id = sa.Column(sa.ForeignKey('bot_product.id', ondelete='CASCADE', onupdate='CASCADE'),
                           primary_key=False, nullable=False, comment='id категории продукта')
