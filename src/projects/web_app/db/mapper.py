from typing import TypeVar, Type

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel


T = TypeVar('T', bound=DeclarativeBase)


def pydantic_to_sqlalchemy(
        pydantic_model: BaseModel,
        sqlalchemy_model: Type[T],
        to_update: T | None = None,
) -> T:
    """
    Маппер из Pydantic модели в модель SQLAlchemy. Подходит как для обновления
    существующей, так и для создания новой модели.

    :param pydantic_model: Валидный экземпляр модели Pydantic.
    :param sqlalchemy_model: Класс модели SQLAlchemy.
    :param to_update: Экземпляр модели SQLAlchemy. Если задан, то он будет обновлен.
    :return: Новый или обновленный экземпляр модели SQLAlchemy
    """
    db_model = inspect(sqlalchemy_model)
    model_attrs = {attr.key for attr in db_model.attrs}
    data = {key: value for key, value in pydantic_model.model_dump(exclude_unset=True).items() if key in model_attrs}
    if to_update is not None:
        for key, value in data.items():
            setattr(to_update, key, value)
        return to_update
    else:
        return sqlalchemy_model(**data)
