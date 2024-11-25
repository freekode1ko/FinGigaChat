from pydantic import BaseModel


class Error(BaseModel):
    """Модель ошибки."""
    detail: str
