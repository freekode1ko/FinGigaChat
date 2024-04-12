import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Integer,
    JSON,
    String,
    Table,
    Text,
    Date,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()
metadata = Base.metadata


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    link = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    text_ = Column('text', Text, nullable=False)
    title = Column(Text)
    text_sum = Column(Text)

    article_name_impact = relationship('ArticleNameImpact', back_populates='article')
    relation_client_article = relationship('RelationClientArticle', back_populates='article')
    relation_commodity_article = relationship('RelationCommodityArticle', back_populates='article')
    relation_telegram_article = relationship('RelationTelegramArticle', back_populates='article')


t_bonds = Table(
    'bonds', metadata,
    Column('Название', Text),
    Column('Доходность', Float(53)),
    Column('Осн,', Float(53)),
    Column('Макс,', Float(53)),
    Column('Мин,', Float(53)),
    Column('Изм,', Text),
    Column('Изм, %', Text),
    Column('Время', Text),
    Column('Unnamed: 0', Float(53)),
    Column('Unnamed: 9', Float(53)),
    Column('0', Float(53)),
    Column('1', Text),
    Column('2', Text),
    Column('3', Float(53)),
    Column('4', Text),
    Column('5', Float(53)),
    Column('6', Float(53))
)


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)


t_date_of_last_build = Table(
    'date_of_last_build', metadata,
    Column('date_time', Text)
)


t_eco_global_stake = Table(
    'eco_global_stake', metadata,
    Column('Country', Text),
    Column('Last', Float(53)),
    Column('Previous', Float(53)),
    Column('Reference', Text),
    Column('Unit', Text)
)


t_eco_rus_influence = Table(
    'eco_rus_influence', metadata,
    Column('Дата', Float(53)),
    Column('Ключевая ставка, % годовых', Float(53)),
    Column('Инфляция, % г/г', Float(53)),
    Column('Цель по инфляции, %', Float(53))
)


t_eco_stake = Table(
    'eco_stake', metadata,
    Column('0', Text),
    Column('1', Text)
)


t_exc = Table(
    'exc', metadata,
    Column('Валюта', Text),
    Column('Курс', Text)
)


t_financial_indicators = Table(
    'financial_indicators', metadata,
    Column('name', Text),
    Column('2021', Text),
    Column('2022', Text),
    Column('2023E', Text),
    Column('2024E', Text),
    Column('2025E', Text),
    Column('alias', Text),
    Column('company', Text),
    Column('2020', Float(53)),
    Column('2022E', Float(53)),
    Column('2019', Float(53)),
    Column('2021E', Float(53)),
    Column('id', BigInteger)
)


class Industry(Base):
    __tablename__ = 'industry'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name = Column(Text, nullable=False)

    client = relationship('Client', back_populates='industry')
    commodity = relationship('Commodity', back_populates='industry')
    industry_alternative = relationship('IndustryAlternative', back_populates='industry')
    telegram_channel = relationship('TelegramChannel', back_populates='industry')


t_key_eco = Table(
    'key_eco', metadata,
    Column('id', BigInteger),
    Column('name', Text),
    Column('2021', Text),
    Column('2022', Text),
    Column('2023E', Text),
    Column('2024E', Text),
    Column('alias', Text)
)


class MessageType(Base):
    __tablename__ = 'message_type'
    __table_args__ = {'comment': 'Справочник типов отправленных сообщений (пассивная рассылка, '
                'ответ на запрос такой-то)'}

    id = Column(Integer, primary_key=True, )
    name = Column(String(64), nullable=False)
    is_default = Column(Boolean,)
    description = Column(String(255),)

    message = relationship('Message', back_populates='message_type')


t_metals = Table(
    'metals', metadata,
    Column('Metals', Text),
    Column('Price', Text),
    Column('Day', Text),
    Column('%', Text),
    Column('Weekly', Text),
    Column('Monthly', Text),
    Column('YoY', Text),
    Column('Date', Text)
)


class SourceGroup(Base):
    __tablename__ = 'source_group'
    __table_args__ = {'comment': 'Справочник выделенных подгрупп среди источников'}

    id = Column(Integer, primary_key=True,)
    name = Column(String(64), nullable=False)
    name_latin = Column(String(64), nullable=False)

    parser_source = relationship('ParserSource', back_populates='source_group')


t_report_bon_day = Table(
    'report_bon_day', metadata,
    Column('0', Text),
    Column('1', Text),
    Column('2', Text)
)


t_report_bon_mon = Table(
    'report_bon_mon', metadata,
    Column('0', Text),
    Column('1', Text),
    Column('2', Text)
)


t_report_eco_day = Table(
    'report_eco_day', metadata,
    Column('0', Text),
    Column('1', Text),
    Column('2', Text)
)


t_report_eco_mon = Table(
    'report_eco_mon', metadata,
    Column('0', Text),
    Column('1', Text),
    Column('2', Text)
)


t_report_exc_day = Table(
    'report_exc_day', metadata,
    Column('0', Text),
    Column('1', Text),
    Column('2', Text)
)


t_report_exc_mon = Table(
    'report_exc_mon', metadata,
    Column('0', Text),
    Column('1', Text),
    Column('2', Text)
)


t_report_industry = Table(
    'report_industry', metadata,
    Column('title', Text),
    Column('text', Text),
    Column('date', Text),
    Column('send_flag', Boolean)
)


t_report_met_day = Table(
    'report_met_day', metadata,
    Column('0', Text),
    Column('1', Text),
    Column('2', Text)
)


t_user_log = Table(
    'user_log', metadata,
    Column('id', BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), nullable=False),
    Column('level', Text, nullable=False),
    Column('date', DateTime, nullable=False),
    Column('file_name', Text),
    Column('func_name', Text),
    Column('line_no', Integer),
    Column('message', Text),
    Column('user_id', BigInteger)
)


class Whitelist(Base):
    __tablename__ = 'whitelist'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(Text)
    full_name = Column(Text)
    user_type = Column(Text)
    user_status = Column(Text)
    user_email = Column(Text)
    subscriptions = Column(Text)

    message = relationship('Message', back_populates='user')
    telegram = relationship('TelegramChannel', secondary='user_telegram_subscription', back_populates='user')


class ArticleNameImpact(Base):
    __tablename__ = 'article_name_impact'

    id = Column(Integer, primary_key=True)
    article_id = Column(ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    commodity_impact = Column(JSON)
    client_impact = Column(JSON)
    cleaned_data = Column(Text)

    article = relationship('Article', back_populates='article_name_impact')


class Client(Base):
    __tablename__ = 'client'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name = Column(Text, nullable=False)
    industry_id = Column(ForeignKey('industry.id', onupdate='CASCADE'))

    industry = relationship('Industry', back_populates='client')
    client_alternative = relationship('ClientAlternative', back_populates='client')
    relation_client_article = relationship('RelationClientArticle', back_populates='client')


class Commodity(Base):
    __tablename__ = 'commodity'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name = Column(Text, nullable=False)
    industry_id = Column(ForeignKey('industry.id', onupdate='CASCADE'))

    industry = relationship('Industry', back_populates='commodity')
    commodity_alternative = relationship('CommodityAlternative', back_populates='commodity')
    commodity_pricing = relationship('CommodityPricing', back_populates='commodity')
    relation_commodity_article = relationship('RelationCommodityArticle', back_populates='commodity')


class IndustryAlternative(Base):
    __tablename__ = 'industry_alternative'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    industry_id = Column(ForeignKey('industry.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    other_names = Column(Text)

    industry = relationship('Industry', back_populates='industry_alternative')


class Message(Base):
    __tablename__ = 'message'
    __table_args__ = {'comment': 'Хранилище отправленных пользователям сообщений'}

    id = Column(BigInteger, primary_key=True)
    user_id = Column(ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    message_id = Column(BigInteger, nullable=False)
    message_type_id = Column(ForeignKey('message_type.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    function_name = Column(Text, nullable=False)
    send_datetime = Column(DateTime(True),)

    message_type = relationship('MessageType', back_populates='message')
    user = relationship('Whitelist', back_populates='message')


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


class TelegramChannel(Base):
    __tablename__ = 'telegram_channel'
    __table_args__ = {'comment': 'Справочник telegram каналов, из которых вынимаются новости'}

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    link = Column(String(255), nullable=False)
    industry_id = Column(ForeignKey('industry.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    industry = relationship('Industry', back_populates='telegram_channel')
    user = relationship('Whitelist', secondary='user_telegram_subscription', back_populates='telegram')
    relation_telegram_article = relationship('RelationTelegramArticle', back_populates='telegram')


class ClientAlternative(Base):
    __tablename__ = 'client_alternative'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    client_id = Column(ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    other_names = Column(Text)

    client = relationship('Client', back_populates='client_alternative')


class CommodityAlternative(Base):
    __tablename__ = 'commodity_alternative'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    commodity_id = Column(ForeignKey('commodity.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    other_names = Column(Text)

    commodity = relationship('Commodity', back_populates='commodity_alternative')


class CommodityPricing(Base):
    __tablename__ = 'commodity_pricing'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    commodity_id = Column(ForeignKey('commodity.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    subname = Column(Text, nullable=False)
    unit = Column(Text)
    price = Column(Float(53))
    m_delta = Column(Float(53))
    y_delta = Column(Float(53))
    cons = Column(Float(53))

    commodity = relationship('Commodity', back_populates='commodity_pricing')


class RelationClientArticle(Base):
    __tablename__ = 'relation_client_article'

    client_id = Column(ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    article_id = Column(ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    client_score = Column(Integer)

    article = relationship('Article', back_populates='relation_client_article')
    client = relationship('Client', back_populates='relation_client_article')


class RelationCommodityArticle(Base):
    __tablename__ = 'relation_commodity_article'

    commodity_id = Column(ForeignKey('commodity.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    article_id = Column(ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    commodity_score = Column(Integer)

    article = relationship('Article', back_populates='relation_commodity_article')
    commodity = relationship('Commodity', back_populates='relation_commodity_article')


class RelationTelegramArticle(Base):
    __tablename__ = 'relation_telegram_article'
    __table_args__ = {'comment': 'Связь новостей с telegram каналами'}

    telegram_id = Column(ForeignKey('telegram_channel.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    article_id = Column(ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    telegram_score = Column(Integer)

    article = relationship('Article', back_populates='relation_telegram_article')
    telegram = relationship('TelegramChannel', back_populates='relation_telegram_article')


t_user_telegram_subscription = Table(
    'user_telegram_subscription', metadata,
    Column('user_id', ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False),
    Column('telegram_id', ForeignKey('telegram_channel.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
)


class RAGUserFeedback(Base):
    __tablename__ = 'rag_user_feedback'
    __table_args__ = {'comment': 'Обратная связь от пользователей по работе с RAG-системой'}

    chat_id = Column(BigInteger, primary_key=True)
    bot_msg_id = Column(BigInteger, primary_key=True)
    retriever_type = Column(String(16), nullable=False)
    reaction = Column(Boolean)
    date = Column(DateTime, default=datetime.datetime.now)
    query = Column(Text, nullable=False)
    response = Column(Text)


class ResearchGroup(Base):
    __tablename__ = 'research_group'
    __table_args__ = {'comment': 'Справочник групп, выделенных среди разделов CIB Research'}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(64), nullable=False)


class ResearchSection(Base):
    __tablename__ = 'research_section'
    __table_args__ = {'comment': 'Справочник разделов CIB Research'}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(64), nullable=False)
    dropdown_flag = Column(Boolean, server_default='true')
    research_group_id = Column(ForeignKey('research_group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


class ResearchType(Base):
    __tablename__ = 'research_type'
    __table_args__ = {'comment': 'Справочник типов отчетов CIB Research, на которые пользователь может подписаться'}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True, server_default='')
    research_section_id = Column(ForeignKey('research_section.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    source_id = Column(ForeignKey('parser_source.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


class Research(Base):
    __tablename__ = 'research'
    __table_args__ = {'comment': 'Справочник спаршенных отчетов CIB Research'}

    id = Column(BigInteger, primary_key=True)
    research_type_id = Column(ForeignKey('research_type.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    filepath = Column(Text, nullable=True, server_default='')
    header = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    parse_datetime = Column(DateTime, default=datetime.datetime.now, nullable=False)
    publication_date = Column(Date, default=datetime.date.today, nullable=False)
    news_id = Column(BigInteger, nullable=False)
    is_new = Column(Boolean, server_default='true', comment='Указывает, что новость еще не рассылалась пользователям')


class UserResearchSubscriptions(Base):
    __tablename__ = 'user_research_subscription'
    __table_args__ = {'comment': 'Справочник подписок пользователей на отчеты CIB Research'}

    user_id = Column(ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    research_type_id = Column(ForeignKey('research_type.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)


t_relation_commodity_metals = Table(
    'relation_commodity_metals', metadata,
    Column('commodity_id', ForeignKey('commodity.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
    Column('name_from_source', String(100), primary_key=True),
    Column('source', Text, nullable=False),
    Column('unit', String(10)),
    Column('sub_name', String(100), nullable=False)
)


class CallReports(Base):
    __tablename__ = 'bot_call_reports'
    __table_args__ = {'comment': 'Записи call reports'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, comment='Айди пользователя')
    client = Column(String(255), nullable=False, comment='Клиент')
    report_date = Column(Date, nullable=False, comment='Дата проведения встречи')
    description = Column(Text, nullable=False, comment='Отчет по встрече')
