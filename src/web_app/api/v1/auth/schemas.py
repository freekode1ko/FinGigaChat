from pydantic import BaseModel, Field


class UserData(BaseModel):
    """Модель пользователя на выход."""
    class Config:
        from_attributes = True
        populate_by_name = True
        extra = 'ignore'
    user_id: int = Field(..., alias="id")
    user_email: str = Field(..., alias="email")


class TelegramData(BaseModel):
    """Данные пользователя Telegram, включающие дату открытия формы
    (auth_date) и hash для валидации полученных данных
    """
    id: int
    data: str


class AuthData(BaseModel):
    """Аутентификация пользователя по email"""
    email: str


class AuthConfirmation(BaseModel):
    """Подтверждение пользователя"""
    email: str
    reg_code: str
