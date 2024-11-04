"""Новые таблицы с курсами"""

import sqlalchemy as sa
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ExcType(Base):
    __tablename__ = 'bot_exc_type'
    __table_args__ = {'comment': 'Справочник типов курсов валют'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='id типа')
    name = sa.Column(sa.String(64), nullable=False, comment='Наименование типа курсов валют')
    description = sa.Column(sa.Text(), nullable=True, server_default=sa.text("''::text"), comment='Описание')
    display_order = sa.Column(sa.Integer(), server_default=sa.text('0'), nullable=False, comment='Порядок отображения')


class Exc(Base):
    __tablename__ = 'exc'
    __table_args__ = {'comment': 'Таблица с курсами валют'}

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True, comment='id курса валюты')

    name = sa.Column(sa.String(255), nullable=False, comment='Имя курса валюты')
    name_latin = sa.Column(sa.String(255), nullable=True, comment='Имя eng', server_default=sa.text("''"))
    value = sa.Column(sa.String(255), nullable=True, comment='Значение курса', server_default=sa.text("'-'"))
    description = sa.Column(sa.Text(), nullable=True, server_default=sa.text("''::text"), comment='Описание')
    display_order = sa.Column(sa.Integer(), server_default=sa.text('0'), nullable=False, comment='Порядок отображения')

    exc_type_id = sa.Column(sa.Integer, sa.ForeignKey('bot_exc_type.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False, comment='ID типа курса')
    parser_source_id = sa.Column(sa.ForeignKey('parser_source.id', ondelete='CASCADE', onupdate='CASCADE'),
                                 primary_key=False, nullable=False, comment='id источника данных')
