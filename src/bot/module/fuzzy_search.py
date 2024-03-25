
import pandas as pd
from fuzzywuzzy import process

from db.database import engine
from log.logger_base import Logger


class FuzzyAlternativeNames:
    def __init__(self, logger: Logger.logger):
        self._logger = logger
        self.engine = engine

    def get_subjects_data(self, entities: list[str]) -> dict[str, list[str, int]]:
        """
        Получение словаря с данными о сущностях
        :param entities: список сущностей из бд (industry/client/commodity)
        return: dict(любое из альтернативных имен сущности: [сущность, айди сущности])
        """
        subjects_data = dict()

        for entity in entities:
            df_alternative = pd.read_sql(f'SELECT {entity}_id, other_names FROM {entity}_alternative', con=self.engine)
            df_alternative['other_names'] = df_alternative['other_names'].apply(lambda x: x.split(';'))
            df_alternative.insert(0, 'entity', entity)
            df_alternative = df_alternative.explode('other_names').drop_duplicates(subset='other_names')
            subjects_data.update(df_alternative.set_index('other_names').T.to_dict('list'))

        return subjects_data

    def find_nearest_to_subject(self, subject_name: str, criteria: int = 5) -> list[str]:
        """
        Поиск ближайших похожих имен субъектов
        """
        subject_name = subject_name.lower().strip().replace('"', '')
        subjects_names = list(self.get_subjects_data(['industry', 'client', 'commodity']).keys())

        if not subjects_names:
            return []

        near = process.extract(subject_name, subjects_names)
        nearest = near[0][1]
        names = [i[0] for i in near if i[1] >= (nearest - criteria)]

        return names

    def find_nearest_to_subjects_list(self, subjects_names: list[str]) -> dict[str, list]:
        """
        Поиск ближайших похожих имен субъектов
        :param subjects_names: список имен, для которых нужно найти ближайшие
        return: список словарей с данными по ближайшим именам [dict(ближайшее имя: [сущность, айди сущности])]
        """
        subjects_data = self.get_subjects_data(['industry', 'client', 'commodity'])
        if not subjects_data:
            return dict()

        near_subjects_names = []
        for subject_name in subjects_names:
            subject_name = subject_name.lower().strip().replace('"', '')
            near_subjects_names.append(process.extractOne(subject_name, subjects_data.keys())[0])

        return {near_name: subjects_data[near_name] for near_name in near_subjects_names}


