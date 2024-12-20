from pydantic import Field, TypeAdapter

from api.v1.common_schemas import BaseReadModel, BaseWriteModel


class UserRoleRead(BaseReadModel):
    """Модель роли пользователя на чтение"""

    id: int
    name: str
    description: str | None


class UserRead(BaseReadModel):
    """Модель пользователя на чтение"""

    user_id: int = Field(..., alias="id")
    user_email: str = Field(..., alias="email")
    role_id: int = Field(..., alias="role")
    username: str | None = None
    full_name: str | None = None


class UserUpdate(BaseWriteModel):
    """Модель пользователя на редактирование"""

    role_id: int | None = Field(None, alias="role")


users_adapter = TypeAdapter(list[UserRead])
