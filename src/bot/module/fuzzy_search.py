from typing import Optional

import pandas as pd
from fuzzywuzzy import process

from db.database import engine
from log.logger_base import Logger


class FuzzyAlternativeNames:
    def __init__(self, logger: Logger.logger):
        self._logger = logger
        self.engine = engine

    def get_subjects_names(self, subjects: list[str]) -> list[str]:
        """
        Получение всех альтернативных имен по списку из industry, client, commodity
        """
        subjects_names = []

        for subject in subjects:
            df_alternative = pd.read_sql(f'SELECT {subject}_id, other_names FROM {subject}_alternative', con=self.engine)
            df_alternative['other_names'] = df_alternative['other_names'].apply(lambda x: x.split(';'))
            for subject_id, names in zip(df_alternative[f'{subject}_id'], df_alternative['other_names']):
                subjects_names.extend(names)
        return subjects_names

    def find_nearest_to_subject(self, subject_name: str, criteria: int = 5) -> list[str]:
        """
        Поиск ближайших похожих имен субъектов
        """
        subject_name = subject_name.lower().strip().replace('"', '')
        subjects_names = self.get_subjects_names(['industry', 'client', 'commodity'])

        if not subjects_names:
            return []

        near = process.extract(subject_name, subjects_names)
        nearest = near[0][1]
        names = [i[0] for i in near if i[1] >= (nearest - criteria)]

        return names

    def find_nearest_to_subjects_list(
            self,
            subjects_names: list[str],
            subject_types: Optional[list[str]] = None,
    ) -> list[str]:
        """
        Поиск ближайших похожих имен субъектов

        :param subjects_names: список наименований
        :param subject_types: список из строк ['industry', 'client', 'commodity']
                              (среди данных таблиц идет поиск ближайших названий)
        """
        all_types = ['industry', 'client', 'commodity']
        subject_types = subject_types or all_types
        subject_types = list(filter(lambda x: x in all_types, subject_types))
        db_subjects_names = self.get_subjects_names(subject_types)

        if not subjects_names:
            return []

        near_subjects = []

        for subject_name in subjects_names:
            subject_name = subject_name.lower().strip().replace('"', '')
            near_subjects.append(process.extractOne(subject_name, db_subjects_names)[0])

        return near_subjects
