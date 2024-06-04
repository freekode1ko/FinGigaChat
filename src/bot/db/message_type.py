"""Запросы к бд связанные с типами сообщений"""
import pandas as pd

from db import database


class MessageType:
    """Типы сообщений"""

    __table_name__ = 'message_type'

    def __init__(self):
        self.__size: int = 0
        self.__types: pd.DataFrame = pd.DataFrame()
        self.__default: dict = {}

        self.__initialize__()

    def __initialize__(self) -> None:
        """Инитициалайз"""
        self.__types: pd.DataFrame = self.__get_types()
        self.__default: dict = self.__get_default()
        self.__size: int = len(self.__types)

    def __get_types(self) -> pd.DataFrame:
        """Возвращает DataFrame с данными из таблицы message_type, индекс каждой строки равен id в базе"""
        data = pd.read_sql_table(self.__table_name__, con=database.engine, index_col='id')
        data['id'] = data.index
        return data

    def __get_default(self) -> dict:
        """
        Получить дефолтный

        :return: dict
        """
        if self.__types.empty:
            self.__types = self.__get_types()

        data = self.__types[self.__types['is_default']].to_dict(orient='records')[0]
        return data

    @property
    def size(self) -> int:
        """Размер"""
        return self.__size

    @property
    def default(self) -> dict:
        """Деволт"""
        return self.__default

    @property
    def types(self) -> pd.DataFrame:
        """Типы"""
        return self.__types

    def __getitem__(self, message_type_id: int) -> dict:
        """
        Возвращает словарь с данными о типе сообщения по id типа

        raise KeyError if there is not such message_type_id

        :message_type_id: int
        :return: dict
        """
        return self.__types.loc[message_type_id].to_dict()

    def get_by_name(self, name: str) -> dict:
        """
        Возвращает словарь с данными о типе сообщения по name типа

        raise IndexError if there is not such name
        """
        return self.__types[self.__types['name'] == name].to_dict(orient='records')[0]


message_types = MessageType()
