"""
Неточный поиск по клиентам, сырью, отраслям.
"""
from typing import Optional

import sqlalchemy as sa
from fuzzywuzzy import process
from sqlalchemy.orm import InstrumentedAttribute

from db.database import engine, async_session
from db import models
from log.logger_base import Logger


class FuzzyAlternativeNames:
    """Неточный поиск по клиентам, сырью, отраслям"""

    def __init__(self, logger: Logger.logger):
        """Инициализация экземпляра модуля неточного поиска"""
        self._logger = logger

        self.tables_with_alternative_names_and_pk_colum = [
            (models.IndustryAlternative, models.IndustryAlternative.industry_id),
            (models.CommodityAlternative, models.CommodityAlternative.commodity_id),
            (models.ClientAlternative, models.ClientAlternative.client_id),
        ]

    @staticmethod
    async def get_subjects_names(
            subjects: list[tuple[models.Base, InstrumentedAttribute]],
            with_id: bool = False,
    ) -> list[tuple[int, str] | str]:
        """
        Получение всех альтернативных имен из таблиц

        :param subjects: список таблиц, из которых выгружает альт имена
        :param with_id: нужно ли добавлять айди к клиентам
        :returns: Все альт имена таблиц subjects
        """
        subjects_names = []

        async with async_session() as session:
            for subject in subjects:
                if with_id:
                    data = await session.execute(sa.select(subject[1], subject[0].other_name))
                    data = data.fetchall()
                else:
                    data = await session.execute(sa.select(subject[0].other_name))
                    data = data.scalars()
                subjects_names.extend(data)
        return subjects_names

    async def find_nearest_to_subject(
            self,
            subject_name: str,
            criteria: int = 5,
            subject_types: Optional[list[models.Base]] = None,
    ) -> list[str]:
        """
        Поиск ближайших похожих имен субъектов

        :param subject_name: Наименование субъекта
        :param criteria: отклонение от значения схожести максимально близкого слова к имени субъекта,
                         в пределах отклонения выдается выборка
        :param subject_types: список из строк ['industry', 'client', 'commodity']
                              (среди данных таблиц идет поиск ближайших названий)
        :returns: Список имен, похожих на наименование субъекта
        """
        subject_types = self.tables_with_alternative_names_and_pk_colum \
            if subject_types is None else [x for x in self.tables_with_alternative_names_and_pk_colum if x[0] in subject_types]

        subject_name = subject_name.lower().strip().replace('"', '')
        subjects_names = await self.get_subjects_names(subject_types)

        if not subjects_names:
            return []

        near = process.extract(subject_name, subjects_names)
        nearest = near[0][1]
        names = [i[0] for i in near if i[1] >= (nearest - criteria)]

        return names

    async def find_nearest_to_subjects_list(
            self,
            subjects_names: list[str],
            subject_types: Optional[list[models.Base]] = None,
    ) -> list[str]:
        """
        Поиск ближайших похожих имен субъектов

        :param subjects_names: список наименований
        :param subject_types: список из строк ['industry', 'client', 'commodity']
                              (среди данных таблиц идет поиск ближайших названий)
        :returns: Список ближайших похожих имен субъектов
        """
        subject_types = self.tables_with_alternative_names_and_pk_colum \
            if subject_types is None else [x for x in self.tables_with_alternative_names_and_pk_colum if x[0] in subject_types]
        subject_types = [x for x in subject_types if x in self.tables_with_alternative_names_and_pk_colum]
        db_subjects_names = await self.get_subjects_names(subject_types)

        if not subjects_names:
            return []

        near_subjects = []

        for subject_name in subjects_names:
            subject_name = subject_name.lower().strip().replace('"', '')
            near_subjects.append(process.extractOne(subject_name, db_subjects_names)[0])

        return near_subjects

    async def find_subjects_id_by_name(
            self,
            name: str,
            score: int = 80,
            subject_types: Optional[list[models.Base]] = None,
    ) -> list[int]:
        """
        Поиск ближайших похожих имен из таблиц subject_types по имени

        :param name:            Имя клиента/сырьевого товара/отрасли
        :param score:           Процент совпадения из библиотеки fuzzywuzzy для параметра score_cutoff
        :param subject_types:   Список таблиц, среди которых идет поиск ближайших названий
        :return:                Список наиболее подходящих айдишников клиентов/сырья/отраслей
        """
        models_to_search = self.tables_with_alternative_names_and_pk_colum \
            if subject_types is None else [x for x in self.tables_with_alternative_names_and_pk_colum if x[0] in subject_types]
        if not (subjects_names := await self.get_subjects_names(models_to_search, with_id=True)):
            return []

        client_name = name.lower().strip().replace('"', '')
        matches = process.extractBests(client_name, [_[1] for _ in subjects_names], score_cutoff=score)

        return [j[0] for j in subjects_names if j[1] in [i[0] for i in matches]]
