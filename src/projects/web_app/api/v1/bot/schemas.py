from datetime import datetime

from pydantic import Field

from api.v1.common_schemas import BaseReadModel, BaseWriteModel


class MessageType(BaseReadModel):
    """Тип сообщения в боте"""
    id: int
    name: str
    is_default: bool
    description: str


class BotInfoRead(BaseReadModel):
    """Информация о боте, которая может быть отредактирована администраторами"""
    name: str
    bio: str


class MessageCreate(BaseWriteModel):
    """Схема для создания сообщения"""
    text: str = Field(min_length=1)


class MessageRead(BaseReadModel):
    """Схема для ответов с сообщениями"""
    id: int
    text: str
    send_datetime: datetime
    message_type: MessageType
