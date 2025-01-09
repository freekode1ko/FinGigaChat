from api.v1.common_schemas import BaseReadModel, BaseWriteModel


class SettingsRead(BaseReadModel):
    """Схема для вывода настроек из Redis на чтение"""

    key: str
    name: str
    value: str


class SettingsUpdate(BaseWriteModel):
    """Схема для обновления настроек в Redis"""

    value: str
