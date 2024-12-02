from fastapi import Query
from pydantic import BaseModel, ConfigDict

from db.pagination import Pagination


class BaseReadModel(BaseModel):
    """Базовая схема модели на чтение"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class BaseWriteModel(BaseModel):
    """Базовая схема модели на запись (создание / обновление)"""
    model_config = ConfigDict(str_strip_whitespace=True, extra='ignore', allow_inf_nan=False)


class Error(BaseModel):
    """Модель ошибки."""
    detail: str


class PaginationParams(BaseModel):
    """
    Параметры пагинации.

    Метод parse_params() выполняет преобразование параметров и возвращает
    экземпляр класса Pagination, который содержит атрибуты limit и offset.
    """
    page: int = Query(1, ge=1, description="Номер страницы")
    size: int = Query(10, ge=1, le=100, description="Размер страницы")

    def parse_params(self) -> Pagination:
        return Pagination(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )
