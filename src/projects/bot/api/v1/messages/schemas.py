"""Схемы для API messages"""
from pydantic import BaseModel, Field


class BaseMessage(BaseModel):
    """Модель пользователя на выход."""

    # user_id: int
    message_text: str
    parse_mode: str = 'HTML'
    user_roles: list[int] = Field(default_factory=list)
    message_type_d: int = 1
    function_name: str = ''
