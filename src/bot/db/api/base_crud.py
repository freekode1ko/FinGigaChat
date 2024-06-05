"""Классы для CRUD"""

import logging
from typing import Any, Generic, Optional, Protocol, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.orm import InstrumentedAttribute

from db import database


class BaseProtocol(Protocol):
    """Base protocol that ORM model should follow."""

    id: int  # noqa:A003


Orm = TypeVar('Orm', bound=BaseProtocol)


class BaseCRUD(Generic[Orm]):
    """Класс, который создает объекты для взаимодействия с таблицей Orm"""

    _table: Type[Orm]

    def __init__(self, table: Type[Orm], order: InstrumentedAttribute, logger: logging.Logger) -> None:
        """
        Объект, предоставляющего интерфейс для взаимодействия с таблицей table

        :param table: Класс ORM sqlalchemy, представляющий таблицу в БД
        :param order: Используется для выражения ORDER BY
        :param logger: Логгер (синхронный)
        """
        self._table = table
        self._order = order
        self._logger = logger
        self._async_session_maker = database.async_session

        self.columns = [i.name for i in self._table.__table__.columns]
        self.fields = [getattr(self._table, c) for c in self.columns]

    async def create(self, item: Orm) -> Optional[Orm]:
        """
        Добавляет с БД запись о новом объекте

        поле id генерируется автоматически
        Если одно из полей item будет нарушать любое ограничение таблицы self._table, то вернется None

        :param item: Объект ORM sqlalchemy, у которого заданы значения обязательных столбцов таблицы
        :returns: Возвращает либо сам объект, который был добавлен в БД, либо None
        """
        async with self._async_session_maker() as session:
            try:
                session.add(item)
                await session.commit()
            except Exception as e:
                self._logger.error(f'При добавлении объекта {item} произошла ошибка: %s', e)
                await session.rollback()
                return None
            else:
                await session.refresh(item)
                return item

    async def get(self, _id: int) -> Optional[Orm]:
        """
        Возвращает объект ORM sqlalchemy, если _id присутствует в таблице self._table иначе возвращает None

        :param _id: значение primary key таблицы self._table, по которому вынимается запись из таблицы
        :returns: Возвращает либо сам объект, который есть в БД, либо None
        """
        async with self._async_session_maker() as session:
            item = await session.get(self._table, _id)
            return item

    async def get_all(self) -> list[Orm]:
        """
        Выгрузка всех объектов ORM sqlalchemy из таблицы self._table

        :returns: список объектов ORM sqlalchemy
        """
        async with self._async_session_maker() as session:
            result = await session.scalars(select(self._table).order_by(self._order))
            return list(result)

    async def update(self, _id: int, update_dict: dict[str, Any]) -> Optional[Orm]:
        """
        Обновляет обновляет данные в БД в таблице self.table по id == _id

        :param _id: id объекта, который необходимо обновить
        :param update_dict: данные для обновления в виде словаря, где ключ это название обновляемой колонки
        :returns: Возвращает либо сам объект, который есть в БД, либо None
        """
        async with self._async_session_maker() as session:
            try:
                await session.execute(update(self._table).where(self._table.id == _id).values(**update_dict))
                await session.commit()
            except Exception as e:
                self._logger.error(f'При обновлении объекта с id={_id} данными {update_dict} произошла ошибка: %s', e)
                await session.rollback()
                return None
            else:
                item = await session.get(self._table, _id)
                return item

    async def delete(self, _id: int) -> bool:
        """
        Удаляет объект с id == _id, если _id присутствует в таблице self._table

        :returns: Возвращает True, если объект был удален, иначе False
        """
        async with self._async_session_maker() as session:
            stmt = delete(self._table).where(self._table.id == _id).returning(self._table.id)
            item_id = await session.execute(stmt)
            await session.commit()
            return item_id.scalar_one_or_none() is not None
