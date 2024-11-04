from pydantic import BaseModel, Field, ConfigDict


class UserData(BaseModel):
    """Модель пользователя на выход."""
    model_config = ConfigDict(from_attributes = True, populate_by_name = True)

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
