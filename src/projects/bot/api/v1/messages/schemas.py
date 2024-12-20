from enum import StrEnum

from pydantic import BaseModel, Field, ConfigDict


class ParseMethods(StrEnum):

    html = "HTML"
    markdown = "Markdown"

class BaseMessage(BaseModel):
    """Модель пользователя на выход."""

    user_id: int
    message_text: str
    parse_mode: ParseMethods = ParseMethods.html
    user_roles: list[int] = None

