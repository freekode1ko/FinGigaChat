"""Модуль нахождения дублирующих отчетов."""
import datetime as dt
from typing import ClassVar

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


class Deduplication:
    """Дедубликация отчетов."""

    MAX_DAYS_LIM: ClassVar[dt.timedelta] = dt.timedelta(days=3)  # порог определения старого отчета: лежит в БД более 3 дней
    BIG_REPORT_LEN: ClassVar[int] = 3_000  # порог определения большого отчета: длина больше BIG_REPORT_LEN символов
    THRESHOLD: ClassVar[float] = 0.85  # чем выше граница, тем сложнее посчитать отчет уникальным
    ADD_TO_OLD_THRESHOLD: ClassVar[float] = 0.1  # на сколько увеличить threshold, если между отчетами разница > MAX_TIME_LIM
    REDUCE_TO_OLD_THRESHOLD: ClassVar[float] = 0.05  # на сколько уменьшить threshold, если длина отчета больше

    def __init__(self):
        self.vectorizer = TfidfVectorizer()

    def deduplicate_inner(self, df_reports: pd.DataFrame) -> pd.DataFrame:
        """
        Дедубликация внутри батча отчетов: проставление parent_report_id для дублей.

        :param df_reports: Датафрейм с отчетами.
        :return:           Датафрейм без дублей.
        """
        if df_reports.empty or len(df_reports) == 1:
            return df_reports

        indices = df_reports.index
        x_tf_idf = self.vectorizer.fit_transform(df_reports['lemma_text']).toarray()

        for i_index in indices[:-1]:

            i_text_len = len(df_reports['text'][i_index])
            for j_index in indices[i_index + 1:]:

                j_text_len = len(df_reports['text'][j_index])
                current_threshold = self.THRESHOLD

                # если разница между отчетами больше N дней, то увеличиваем трешхолд схожести
                if abs(df_reports['publication_date'][i_index] - df_reports['publication_date'][j_index]) > self.MAX_DAYS_LIM:
                    current_threshold += self.ADD_TO_OLD_THRESHOLD
                # если отчет большой, то уменьшаем трешхолд
                if i_text_len > self.BIG_REPORT_LEN:
                    current_threshold -= self.REDUCE_TO_OLD_THRESHOLD

                if x_tf_idf[i_index, :].dot(x_tf_idf[j_index, :].T) > current_threshold:
                    # присваиваем parent_report_id отчету с наименьшей длиной
                    if i_text_len < j_text_len:
                        df_reports.at[i_index, 'parent_report_id'] = df_reports['report_id'][j_index]
                    else:
                        df_reports.at[j_index, 'parent_report_id'] = df_reports['report_id'][i_index]
                    break

        return df_reports
