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

    author_id: int
    message_text: str
    message_files: list[int] | None = Field(default_factory=list)
    message_type_id: int = 1
    user_roles: list[int] = Field(default_factory=list)
    users_emails: list[str] = Field(default_factory=list)
    users_ids: list[int] = Field(default_factory=list)
    parse_mode: str = 'HTML'
    function_name: str = ''


class BaseBroadcast(BaseModel):
    """Модель сообщений"""

    author_id: int
    message_text: str
    message_files: list[int] = Field(default_factory=list)
    message_type_id: int = 1
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

