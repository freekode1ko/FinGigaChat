from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict

from db import models


class ParseMethods(StrEnum):

    html = "HTML"
    markdown = "Markdown"


class BroadcastFile(BaseModel):
    name: str


class CreateBroadcast(BaseModel):
    """Модель сообщений"""

    message_text: str
    message_files: list[int] = Field(default_factory=list)
    message_type_id: int = 1
    user_roles: list[int] = Field(default_factory=list)
    parse_mode: str = 'HTML'
    function_name: str = ''


class BaseBroadcast(BaseModel):
    """Модель сообщений"""

    message_text: str
    message_files: list[int] = Field(default_factory=list)
    message_type_id: int = 1
    user_roles: list[int] = Field(default_factory=list)
    create_at: datetime
    parse_mode: str = 'HTML'
    function_name: str = ''


class FullBroadcast(BaseBroadcast):
    deleted_at: datetime | None = None
    broadcast_id: int


class BroadcastWithVersions(FullBroadcast):
    versions: list[BaseBroadcast]


class BroadcastList(BaseModel):
    broadcasts: list[BaseBroadcast | FullBroadcast]

    # @classmethod
    # def from_dict(cls, data: dict):
    #     """Создать экземпляр класса из словаря."""
    #
    #     files_data = data.get('files', [])
    #     files = [MessageFile(**file) for file in files_data] if files_data else []
    #
    #     return cls(
    #         user_id=data['user_id'],
    #         message_text=data['message_text'],
    #         files=files,
    #         parse_mode=data.get('parse_mode', ParseMethods.html)
    #     )

    # @classmethod
    # def from_db(cls, data: models.Broadcast):
    #     """Создать экземпляр класса из строки базы данных."""
    #
    #     user_id, message_text, files_data, parse_mode = db_row
    #     files = [MessageFile(name=file) for file in files_data] if files_data else []
    #
    #     return cls(
    #         user_id=user_id,
    #         message_text=message_text,
    #         files=files,
    #         parse_mode=ParseMethods(parse_mode) if parse_mode else ParseMethods.html
    #     )
