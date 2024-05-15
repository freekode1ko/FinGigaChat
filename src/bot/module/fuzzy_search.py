from typing import Optional

import sqlalchemy as sa
from fuzzywuzzy import process

from db.database import engine, async_session
from db import models
from log.logger_base import Logger


class FuzzyAlternativeNames:
    def __init__(self, logger: Logger.logger):
        self._logger = logger
        self.engine = engine

        self.tables_with_alternative_names = [
            models.IndustryAlternative,
            models.CommodityAlternative,
            models.ClientAlternative,
        ]

    @staticmethod
    async def get_subjects_names(subjects: list[models.Base]) -> list[str]:
        """
        Получение всех альтернативных имен по списку из industry, client, commodity
        """
        subjects_names = []

        async with async_session() as session:
            for subject in subjects:
                data = await session.execute(sa.select(subject.other_name))
                subjects_names.extend(data.scalars())
        return subjects_names

    async def find_nearest_to_subject(self, subject_name: str, criteria: int = 5) -> list[str]:
        """
        Поиск ближайших похожих имен субъектов
        """
        subject_name = subject_name.lower().strip().replace('"', '')
        subjects_names = await self.get_subjects_names(self.tables_with_alternative_names)

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
        """
        subject_types = subject_types or self.tables_with_alternative_names
        subject_types = list(filter(lambda x: x in self.tables_with_alternative_names, subject_types))
        db_subjects_names = await self.get_subjects_names(subject_types)

        if not subjects_names:
            return []

        near_subjects = []

        for subject_name in subjects_names:
            subject_name = subject_name.lower().strip().replace('"', '')
            near_subjects.append(process.extractOne(subject_name, db_subjects_names)[0])

        return near_subjects
