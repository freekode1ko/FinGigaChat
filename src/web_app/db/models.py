import sqlalchemy as sa
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,

)
from sqlalchemy.orm import declarative_base


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
    date_start = Column(DateTime, nullable=False, comment='Время начала встречи (UTC)')
    date_end = Column(DateTime, nullable=False, comment='Время окончания встречи (UTC)')
    timezone = Column(Integer, comment='Таймзона пользователя во время использования web app', nullable=False)
    is_notify_first = Column(Boolean, server_default=sa.text('false'),
                             comment='Указывает на отправку первого уведомления')
    is_notify_second = Column(Boolean, server_default=sa.text('false'),
                              comment='Указывает на отправку второго уведомления')
    is_notify_last = Column(Boolean, server_default=sa.text('false'),
                            comment='Указывает на отправку последнего уведомления')
    description = Column(Text, comment='Описание встречи')
