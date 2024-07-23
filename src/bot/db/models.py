"""Модели таблиц всех сервисов"""
import datetime

import sqlalchemy as sa
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Identity,
    Integer,
    JSON,
    String,
    Table,
    Text
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, relationship

from constants import enums
from constants.enums import FormatType


class Base(DeclarativeBase):

    len_of_any_str_field = 100

    def __repr__(self):
        """Для более удобного отображения в дебаге"""
        cols = []
        for col in self.__table__.columns.keys():
            cols.append(f'{col}={value[:self.len_of_any_str_field] if isinstance(value := getattr(self, col), str) else value}')
        return f'<{self.__class__.__name__} {", ".join(cols)}›'


metadata = Base.metadata
mapper_registry = sa.orm.registry(metadata=metadata)


class Article(Base):
    __tablename__ = 'article'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    link = Column(Text, nullable=False, comment='Ссылка на новость')
    date = Column(DateTime, nullable=False, comment='Дата и время публикации новости')
    text_ = Column('text', Text, nullable=False, comment='Исходный текст новости')
    title = Column(Text, comment='Заголовок новости (если заголовка не было, то его формирует гигачат)')
    text_sum = Column(Text, comment='Сформированная гигачатом сводка по новости')

    article_name_impact = relationship('ArticleNameImpact', back_populates='article')
    relation_client_article = relationship('RelationClientArticle', back_populates='article')
    relation_commodity_article = relationship('RelationCommodityArticle', back_populates='article')
    relation_telegram_article = relationship('RelationTelegramArticle', back_populates='article')


class Bonds(Base):
    __tablename__ = 'bonds'
    __table_args__ = {'comment': 'Котировки'}

    name = Column('Название', Text)
    profitability = Column('Доходность', Float(53))
    main_value = Column('Осн,', Float(53))
    max_value = Column('Макс,', Float(53))
    min_value = Column('Мин,', Float(53))
    change = Column('Изм,', Text)
    change_percent = Column('Изм, %', Text)
    time = Column('Время', Text)
    unnamed_0 = Column('Unnamed: 0', Float(53))
    unnamed_9 = Column('Unnamed: 9', Float(53))
    col_0 = Column('0', Float(53))
    col_1 = Column('1', Text)
    col_2 = Column('2', Text)
    col_3 = Column('3', Float(53))
    col_4 = Column('4', Text)
    col_5 = Column('5', Float(53))
    col_6 = Column('6', Float(53))


class DateOfLastBuild(Base):
    __tablename__ = 'date_of_last_build'

    id = Column(Integer, primary_key=True)
    date_time = Column(Text)


class EcoGlobalStake(Base):
    __tablename__ = 'eco_global_stake'

    id = Column(Integer, primary_key=True)
    country = Column('Country', Text)
    last = Column('Last', Float(53))
    previous = Column('Previous', Float(53))
    reference = Column('Reference', Text)
    unit = Column('Unit', Text)


class EcoRusInfluence(Base):
    __tablename__ = 'eco_rus_influence'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column('Дата', Float(53))
    key_rate_annual = Column('Ключевая ставка, % годовых', Float(53))
    inflation_annual = Column('Инфляция, % г/г', Float(53))
    inflation_target = Column('Цель по инфляции, %', Float(53))


class EcoStake(Base):
    __tablename__ = 'eco_stake'

    id = Column(Integer, primary_key=True)
    col_0 = Column('0', Text)
    col_1 = Column('1', Text)


class FinancialIndicator(Base):
    __tablename__ = 'financial_indicators'

    id = Column(BigInteger, primary_key=True)
    name = Column(Text)
    year_2021 = Column('2021', Text)
    year_2022 = Column('2022', Text)
    year_2023_e = Column('2023E', Text)
    year_2024_e = Column('2024E', Text)
    year_2025_e = Column('2025E', Text)
    alias = Column(Text)
    company = Column(Text)
    year_2020 = Column('2020', Float(53))
    year_2022_e = Column('2022E', Float(53))
    year_2019 = Column('2019', Float(53))
    year_2021_est = Column('2021E', Float(53))


class Industry(Base):
    __tablename__ = 'industry'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name = Column(Text, nullable=False)
    display_order = Column(Integer(), server_default=sa.text('0'),
                           nullable=False, comment='Порядок отображения отраслей')

    client = relationship('Client', back_populates='industry')
    commodity = relationship('Commodity', back_populates='industry')
    industry_alternative = relationship('IndustryAlternative', back_populates='industry')


class KeyEco(Base):
    __tablename__ = 'key_eco'

    id = Column(BigInteger, primary_key=True)
    name = Column(Text)
    year_2021 = Column('2021', Text)
    year_2022 = Column('2022', Text)
    year_2023_e = Column('2023E', Text)
    year_2024_e = Column('2024E', Text)
    alias = Column(Text)


class MessageType(Base):
    __tablename__ = 'message_type'
    __table_args__ = {
        'comment': 'Справочник типов отправленных сообщений (пассивная рассылка, ответ на запрос такой-то)'
    }

    id = Column(Integer, primary_key=True, )
    name = Column(String(64), nullable=False)
    is_default = Column(Boolean,)
    description = Column(String(255),)

    message = relationship('Message', back_populates='message_type')


class Metals(Base):
    __tablename__ = 'metals'

    id = Column(BigInteger, primary_key=True)
    metal = Column('Metals', Text)
    price = Column('Price', Float(53))
    day = Column('Day', Float(53))
    percentage = Column('%', Text)
    weekly = Column('Weekly', Text)
    monthly = Column('Monthly', Text)
    year_over_year = Column('YoY', Text)
    date = Column('Date', Text)


class SourceGroup(Base):
    __tablename__ = 'source_group'
    __table_args__ = {'comment': 'Справочник выделенных подгрупп среди источников'}

    id = Column(Integer, primary_key=True,)
    name = Column(String(64), nullable=False)
    name_latin = Column(String(64), nullable=False)

    parser_source = relationship('ParserSource', back_populates='source_group')


class ReportBonDay(Base):
    __tablename__ = 'report_bon_day'

    id = Column(BigInteger, primary_key=True)
    col_0 = Column('0', Text)
    col_1 = Column('1', Text)
    col_2 = Column('2', Text)


class ReportBonMon(Base):
    __tablename__ = 'report_bon_mon'

    id = Column(BigInteger, primary_key=True)
    col_0 = Column('0', Text)
    col_1 = Column('1', Text)
    col_2 = Column('2', Text)


class ReportEcoDay(Base):
    __tablename__ = 'report_eco_day'

    id = Column(BigInteger, primary_key=True)
    col_0 = Column('0', Text)
    col_1 = Column('1', Text)
    col_2 = Column('2', Text)


class ReportEcoMon(Base):
    __tablename__ = 'report_eco_mon'

    id = Column(BigInteger, primary_key=True)
    col_0 = Column('0', Text)
    col_1 = Column('1', Text)
    col_2 = Column('2', Text)


class ReportExcDay(Base):
    __tablename__ = 'report_exc_day'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    col_0 = Column('0', Text)
    col_1 = Column('1', Text)
    col_2 = Column('2', Text)


class ReportExcMon(Base):
    __tablename__ = 'report_exc_mon'

    id = Column(BigInteger, primary_key=True)
    col_0 = Column('0', Text)
    col_1 = Column('1', Text)
    col_2 = Column('2', Text)


class ReportMetDay(Base):
    __tablename__ = 'report_met_day'

    id = Column(BigInteger, primary_key=True)
    col_0 = Column('0', Text)
    col_1 = Column('1', Text)
    col_2 = Column('2', Text)


class UserLog(Base):
    __tablename__ = 'user_log'

    id = Column(BigInteger, primary_key=True)
    level = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    file_name = Column(Text)
    func_name = Column(Text)
    line_no = Column(Integer)
    message = Column(Text)
    user_id = Column(BigInteger)


class Whitelist(Base):
    __tablename__ = 'whitelist'

    user_id = Column(BigInteger, primary_key=True)
    username = Column(Text)
    full_name = Column(Text)
    user_type = Column(Text)
    user_status = Column(Text)
    user_email = Column(Text, server_default=sa.text("''::text"))

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

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name = Column(Text, nullable=False)
    navi_link = Column(Text, nullable=True, server_default='')
    industry_id = Column(ForeignKey('industry.id', onupdate='CASCADE'), nullable=True)

    industry = relationship('Industry', back_populates='client')
    client_alternative = relationship('ClientAlternative', back_populates='client')
    relation_client_article = relationship('RelationClientArticle', back_populates='client')
    beneficiaries = relationship('Beneficiary', secondary='relation_client_beneficiary', back_populates='clients')


class Commodity(Base):
    __tablename__ = 'commodity'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    name = Column(Text, nullable=False)
    industry_id = Column(ForeignKey('industry.id', onupdate='CASCADE'), nullable=True)

    industry = relationship('Industry', back_populates='commodity')
    commodity_alternative = relationship('CommodityAlternative', back_populates='commodity')
    commodity_pricing = relationship('CommodityPricing', back_populates='commodity')
    relation_commodity_article = relationship('RelationCommodityArticle', back_populates='commodity')


class IndustryAlternative(Base):
    __tablename__ = 'industry_alternative'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    industry_id = Column(ForeignKey('industry.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    other_name = Column(Text)

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
    name = Column(String(128), nullable=False, comment='Название телеграм канала')
    link = Column(String(255), nullable=False, comment='Ссылка на телеграм канал')
    section_id = Column(ForeignKey('bot_telegram_section.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                        comment='Связь телеграм канала с разделом (например, отрасль "Недвижимость")')

    section = relationship('TelegramSection', back_populates='telegram_channel')
    user = relationship('Whitelist', secondary='user_telegram_subscription', back_populates='telegram')
    relation_telegram_article = relationship('RelationTelegramArticle', back_populates='telegram')


class ClientAlternative(Base):
    __tablename__ = 'client_alternative'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    client_id = Column(ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    other_name = Column(Text)

    client = relationship('Client', back_populates='client_alternative')


class CommodityAlternative(Base):
    __tablename__ = 'commodity_alternative'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
    commodity_id = Column(ForeignKey('commodity.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    other_name = Column(Text)

    commodity = relationship('Commodity', back_populates='commodity_alternative')


class CommodityPricing(Base):
    __tablename__ = 'commodity_pricing'

    id = Column(Integer, Identity(always=True, start=1, increment=1, minvalue=1,
                maxvalue=2147483647, cycle=False, cache=1), primary_key=True)
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

    client_id = Column(ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'),
                       primary_key=True, nullable=False)
    article_id = Column(ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    client_score = Column(Integer)

    article = relationship('Article', back_populates='relation_client_article')
    client = relationship('Client', back_populates='relation_client_article')


class RelationCommodityArticle(Base):
    __tablename__ = 'relation_commodity_article'

    commodity_id = Column(ForeignKey('commodity.id', ondelete='CASCADE', onupdate='CASCADE'),
                          primary_key=True, nullable=False)
    article_id = Column(ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    commodity_score = Column(Integer)

    article = relationship('Article', back_populates='relation_commodity_article')
    commodity = relationship('Commodity', back_populates='relation_commodity_article')


class RelationTelegramArticle(Base):
    __tablename__ = 'relation_telegram_article'
    __table_args__ = {'comment': 'Связь новостей с telegram каналами'}

    telegram_id = Column(ForeignKey('telegram_channel.id', ondelete='CASCADE', onupdate='CASCADE'),
                         primary_key=True, nullable=False)
    article_id = Column(ForeignKey('article.id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)
    telegram_score = Column(Integer)

    article = relationship('Article', back_populates='relation_telegram_article')
    telegram = relationship('TelegramChannel', back_populates='relation_telegram_article')


t_user_telegram_subscription = Table(
    'user_telegram_subscription', metadata,
    Column('user_id', ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'),
           primary_key=True, nullable=False),
    Column('telegram_id', ForeignKey('telegram_channel.id', ondelete='CASCADE', onupdate='CASCADE'),
           primary_key=True, nullable=False)
)


class UserTelegramSubscriptions:
    pass


mapper_registry.map_imperatively(UserTelegramSubscriptions, t_user_telegram_subscription)


class RAGUserFeedback(Base):
    __tablename__ = 'rag_user_feedback'
    __table_args__ = {'comment': 'Обратная связь от пользователей по работе с RAG-системой'}

    chat_id = Column(BigInteger, primary_key=True, comment='ID чата с пользователем')
    bot_msg_id = Column(BigInteger, primary_key=True, comment='ID сообщения бота')
    retriever_type = Column(String(16), nullable=False, comment='Тип ретривера: новости, господдержка, гигачат')
    reaction = Column(Boolean, comment='Обратная связь от пользователя: True - положительная, False - отрицательная')
    date = Column(DateTime, default=datetime.datetime.now, comment='Дата сообщения от бота')
    query = Column(Text, nullable=False, comment='Запрос пользователя')
    response = Column(Text, comment='Ответ на запрос пользователя')
    history_query = Column(Text, comment='Перефразированный на истории диалога запрос пользователя')
    history_response = Column(Text, comment='Ответ на перефразированный на истории диалога запрос пользователя')
    rephrase_query = Column(Text, comment='Перефразированный запрос пользователя')
    rephrase_response = Column(Text, comment='Ответ на перефразированный запрос пользователя')


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
    display_order = Column(Integer, nullable=True, server_default='0')
    dropdown_flag = Column(Boolean, server_default='true')
    section_type = Column(
        Integer,
        server_default=str(enums.ResearchSectionType.default.value),
        comment='тип раздела из enums.ResearchSectionType (зависит формирование меню аналитики)',
    )
    research_group_id = Column(ForeignKey('research_group.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)


class ResearchType(Base):
    __tablename__ = 'research_type'
    __table_args__ = {'comment': 'Справочник типов отчетов CIB Research, на которые пользователь может подписаться'}

    id = Column(BigInteger, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True, server_default='')
    summary_type = Column(
        Integer,
        server_default=str(enums.ResearchSummaryType.periodic.value),
        comment=(
            'тип формирования сводки отчетов CIB Research '
            'из enums.ResearchSummaryType (зависит формирование меню аналитики)'
        ),
    )
    research_section_id = Column(ForeignKey('research_section.id', ondelete='CASCADE', onupdate='CASCADE'),
                                 nullable=False)
    source_id = Column(ForeignKey('parser_source.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    researches = relationship('Research', secondary='research_research_type', back_populates='research_type')


class Research(Base):
    __tablename__ = 'research'
    __table_args__ = {'comment': 'Справочник спаршенных отчетов CIB Research'}

    id = Column(BigInteger, primary_key=True)
    filepath = Column(Text, nullable=True, server_default='')
    header = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    parse_datetime = Column(DateTime, default=datetime.datetime.now, nullable=False)
    publication_date = Column(Date, default=datetime.date.today, nullable=False)
    report_id = Column(String(64), nullable=False)
    is_new = Column(Boolean, server_default=sa.text('true'),
                    comment='Указывает, что отчет еще не рассылался пользователям')

    research_type = relationship('ResearchType', secondary='research_research_type', back_populates='researches')


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


class CallReports(Base):
    __tablename__ = 'bot_call_reports'
    __table_args__ = {'comment': 'Записи call reports'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'),
                     primary_key=True, comment='Айди пользователя')
    client = Column(String(255), nullable=False, comment='Клиент')
    report_date = Column(Date, nullable=False, comment='Дата проведения встречи')
    description = Column(Text, nullable=False, comment='Отчет по встрече')


class FinancialSummary(Base):
    __tablename__ = 'financial_summary'
    __table_args__ = (
        sa.UniqueConstraint('sector_id', 'company_id', 'client_id', name='fin_indicator'),
        {'comment': 'Справочник таблиц с финансовыми показателями клиентов из CIB Research'},
    )

    id = Column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=2147483647,
                                     cycle=False, cache=1), primary_key=True)
    sector_id = Column(Text, nullable=False, comment='ID сектора на cib research')
    company_id = Column(Text, nullable=False, comment='ID клиента на cib research')
    client_id = Column(ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'),
                       nullable=False, comment='ID клиента у нас в БД')
    review_table = Column(Text, nullable=True, comment='Таблица с обзорной таблицей в формате dict')
    pl_table = Column(Text, nullable=True, comment='Таблица с P&L таблицей в формате dict')
    balance_table = Column(Text, nullable=True, comment='Таблица с балансной таблицей в формате dict')
    money_table = Column(Text, nullable=True, comment='Таблица с таблицей денежных потоков в формате dict')


class UserClientSubscriptions(Base):
    __tablename__ = 'user_client_subscription'
    __table_args__ = {'comment': 'Справочник подписок пользователей на клиентов'}

    user_id = Column(ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    client_id = Column(ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)


class UserCommoditySubscriptions(Base):
    __tablename__ = 'user_commodity_subscription'
    __table_args__ = {'comment': 'Справочник подписок пользователей на сырьевые товары'}

    user_id = Column(ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    commodity_id = Column(ForeignKey('commodity.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)


class UserIndustrySubscriptions(Base):
    __tablename__ = 'user_industry_subscription'
    __table_args__ = {'comment': 'Справочник подписок пользователей на отрасли'}

    user_id = Column(ForeignKey('whitelist.user_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    industry_id = Column(ForeignKey('industry.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)


class IndustryDocuments(Base):
    __tablename__ = 'bot_industry_documents'
    __table_args__ = {'comment': 'Справочник файлов отраслевой аналитики'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='id файла в базе')
    file_name = Column(String(255), nullable=False, comment='Имя файла')
    file_path = Column(Text(), nullable=False, comment='Путь к файлу в системе')
    description = Column(Text(), nullable=True, server_default=sa.text("''::text"), comment='Описание')
    industry_id = Column(ForeignKey('industry.id', ondelete='CASCADE', onupdate='CASCADE'),
                         primary_key=False, nullable=True, comment='id отрасли')
    industry_type = Column(Integer(), nullable=True, server_default=str(enums.IndustryTypes.default.value),
                           comment='тип отрасли')


class Product(Base):
    __tablename__ = 'bot_product'
    __table_args__ = {'comment': 'Справочник продуктов (кредит, GM, ...)'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='id файла в базе')
    parent_id = Column(Integer, ForeignKey('bot_product.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True,
                       comment='ID родительского продукта, который выступает в качестве категории продуктов')
    children = relationship('Product', back_populates='parent')
    parent = relationship('Product', back_populates='children', remote_side=[id])

    name = Column(String(255), nullable=False, comment='Имя продукта (кредит, GM, ...)')
    name_latin = Column(String(255), nullable=True, comment='Имя eng', server_default=sa.text("''"))
    send_documents_format_type = Column(Integer(), server_default=sa.text(str(FormatType.group_files)),
                                        nullable=False, comment='Формат выдачи документов')
    description = Column(Text(), nullable=True, server_default=sa.text("''::text"),
                         comment='Текст сообщения, которое выдается при нажатии на продукт')
    display_order = Column(Integer(), server_default=sa.text('0'), nullable=False, comment='Порядок отображения')

    documents = relationship('ProductDocument')


class ProductDocument(Base):
    __tablename__ = 'bot_product_document'
    __table_args__ = {'comment': 'Справочник файлов продуктов'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='id файла в базе')
    file_path = Column(Text(), nullable=False, comment='Путь к файлу в системе')
    name = Column(String(255), nullable=False, comment='Наименование документа или продуктового предложения')
    description = Column(Text(), nullable=True, server_default=sa.text("''::text"), comment='Описание')
    product_id = Column(ForeignKey('bot_product.id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=False, nullable=False, comment='id категории продукта')


class TelegramGroup(Base):
    __tablename__ = 'bot_telegram_group'
    __table_args__ = {'comment': 'Справочник групп, выделенных среди разделов по телеграм каналам'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='id группы в базе')
    name = Column(String(255), nullable=False, comment='Наименование группы')
    general_name = Column(String(255), nullable=False, comment='Наименование группы для меню новостей')
    display_order = Column(Integer(), server_default=sa.text('0'), nullable=False, comment='Порядок отображения')
    is_show_all_channels = Column(Boolean(), nullable=False, server_default=sa.text("'false'::boolean"),
                                  comment='Указывает, показывать ли сразу все тг каналы, '
                                          'которые косвено связаны с данной группой')

    telegram_section = relationship('TelegramSection', back_populates='telegram_group')


class TelegramSection(Base):
    __tablename__ = 'bot_telegram_section'
    __table_args__ = {'comment': 'Справочник разделов, выделенных среди телеграм каналов'}

    id = Column(Integer, primary_key=True, autoincrement=True, comment='id раздела в базе')
    name = Column(String(255), nullable=False, comment='Наименование раздела')
    display_order = Column(Integer(), server_default=sa.text('0'), nullable=False, comment='Порядок отображения')
    group_id = Column(ForeignKey('bot_telegram_group.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=False,
                      nullable=False, comment='id группы, к которой принадлежит раздел')
    rag_name = Column(String(100), nullable=False, server_default='',
                      comment='Название секции для создания документов в RAG-сервисе')

    telegram_group = relationship('TelegramGroup', back_populates='telegram_section')
    telegram_channel = relationship('TelegramChannel', back_populates='section')


class ResearchResearchType(Base):
    __tablename__ = 'research_research_type'
    __table_args__ = {'comment': 'Cвязь мени ту мени типы ответов и сами отчеты'}

    research_id = Column(ForeignKey('research.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    research_type_id = Column(ForeignKey('research_type.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)


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

    exc_type = relationship('ExcType')
    parser_source = relationship('ParserSource')


class Beneficiary(Base):
    __tablename__ = 'beneficiary'
    __table_args__ = {'comment': 'Таблица с именами бенефициаров'}

    id = Column(Integer(), autoincrement=True, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, comment='ФИО бенефициара')

    alternatives = relationship('BeneficiaryAlternative', back_populates='beneficiary')
    clients = relationship('Client', secondary='relation_client_beneficiary', back_populates='beneficiaries')


class BeneficiaryAlternative(Base):
    __tablename__ = 'beneficiary_alternative'
    __table_args__ = {'comment': 'Таблица с альтернативными именами бенефициаров'}

    id = Column(Integer(), autoincrement=True, primary_key=True)
    beneficiary_id = Column(ForeignKey('beneficiary.id', ondelete='CASCADE', onupdate='CASCADE'),
                            nullable=False, comment='id бенефициара')
    other_name = Column(String(255), nullable=False, unique=True, comment='альтернативное ФИО бенефициара')

    beneficiary = relationship('Beneficiary', back_populates='alternatives')


class RelationClientBeneficiary(Base):
    __tablename__ = 'relation_client_beneficiary'
    __table_args__ = {'comment': 'Таблица отношений бенефициаров к клиентам'}

    client_id = Column(ForeignKey('client.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    beneficiary_id = Column(ForeignKey('beneficiary.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
