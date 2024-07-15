import sqlalchemy as sa
from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    String,
    ARRAY,
    JSON,
    Identity,

)
from sqlalchemy.orm import declarative_base, relationship, deferred

Base = declarative_base()
metadata = Base.metadata


class Whitelist(Base):
    __tablename__ = 'whitelist'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(Text)
    full_name = Column(Text)
    user_type = Column(Text)
    user_status = Column(Text)
    user_email = Column(Text, server_default=sa.text("''::text"))
    subscriptions = Column(Text)


class UserMeeting(Base):
    __tablename__ = 'user_meeting'
    __table_args__ = {'comment': 'Перечень встреч пользователей'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('whitelist.user_id', onupdate='CASCADE', ondelete='CASCADE'), nullable=False)
    theme = Column(Text, nullable=False, default='Напоминание', comment='Тема встречи')
    date_create = Column(DateTime, comment='Время создания встречи (UTC)')
    date_start = Column(DateTime, nullable=False, comment='Время начала встречи (UTC)')
    date_end = Column(DateTime, nullable=False, comment='Время окончания встречи (UTC)')
    timezone = Column(Integer, comment='Таймзона пользователя во время использования web app', nullable=False)
    notify_count = Column(Integer, server_default=sa.text('0'), comment='Количество отправленных напоминаний')
    description = Column(Text, comment='Описание встречи')


class SourceGroup(Base):
    __tablename__ = 'source_group'
    __table_args__ = {'comment': 'Справочник выделенных подгрупп среди источников'}

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    name_latin = Column(String(64), nullable=False)

    parser_source = relationship('ParserSource', back_populates='source_group')


class ParserSource(Base):
    __tablename__ = 'parser_source'
    __table_args__ = {'comment': 'Справочник источников'}

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    alt_names = Column(ARRAY(Text), nullable=False)
    response_format = Column(Text)
    source = Column(Text, nullable=False)
    source_group_id = Column(ForeignKey('source_group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    last_update_datetime = Column(DateTime)
    previous_update_datetime = Column(DateTime)
    params = Column(JSON)
    before_link = Column(Text, nullable=True, server_default='')

    source_group = relationship('SourceGroup', back_populates='parser_source')

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


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    link = Column(Text, nullable=False, comment='Ссылка на новость')
    date = Column(DateTime, nullable=False, comment='Дата и время публикации новости')
    text_ = Column('text', Text, nullable=False, comment='Исходный текст новости')
    title = Column(Text, comment='Заголовок новости (если заголовка не было, то его формирует гигачат)')
    text_sum = Column(Text, comment='Сформированная гигачатом сводка по новости')

    relation_client_article = relationship('RelationClientArticle', back_populates='article')


class RelationClientArticle(Base):
    __tablename__ = 'relation_client_article'

    client_id = Column(ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'),
                       primary_key=True, nullable=False)
    article_id = Column(ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    client_score = Column(Integer)

    article = relationship('Article', back_populates='relation_client_article')
