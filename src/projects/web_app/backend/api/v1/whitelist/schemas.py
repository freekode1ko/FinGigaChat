from pydantic import Field, TypeAdapter

from api.v1.common_schemas import BaseReadModel, BaseWriteModel


class WhitelistRead(BaseReadModel):
    """Схема для вывода записи из белого списка на чтение"""

    user_email: str = Field(..., alias='email')


class WhitelistCreate(BaseWriteModel):
    """Схема для создания новой записи в белом списке"""

    user_email: str = Field(
        ...,
        min_length=9,
        max_length=255,
        pattern=r'\w+@sber(bank)?.ru',
        alias='email'
    )


whitelist_adapter = TypeAdapter(list[WhitelistRead])
