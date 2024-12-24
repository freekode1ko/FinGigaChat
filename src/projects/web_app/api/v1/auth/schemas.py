from pydantic import BaseModel


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
