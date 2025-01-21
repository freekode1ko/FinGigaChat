"""Пагинация"""
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel

from configs import config


class PaginationData(BaseModel):
    page: int
    size: int

    def get_db_limit(self):
        """Получить limit для запроса к БД"""
        return self.size

    def get_db_offset(self):
        """Получить offset для запроса к БД"""
        return self.size * (self.page - 1)

    def get_db_params(self) -> (int, int):
        """Получить сразу limit и offset"""
        return self.get_db_limit(), self.get_db_offset()


def get_pagination_dep(
        page: Annotated[
                int,
                Query(ge=1, description="Номер страницы"),
            ] = 1,
        size: Annotated[
            int,
            Query(ge=1, le=100, description="Размер страницы")
        ] = config.API_PAGINATION_SIZE) -> PaginationData:
    """Dependency для пагинации"""
    return PaginationData(page=page, size=size)

# class PaginationDependency:



