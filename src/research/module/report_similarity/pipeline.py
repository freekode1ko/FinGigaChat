"""Модуль с пайплайном по нахождению похожих отчетов."""
import datetime as dt
import re
from collections import namedtuple
from typing import Any, ClassVar

import pandas as pd

from constants.constants import REPLACE_STMTS
from db.research import get_old_reports_for_period, update_parent_report_ids
from module.report_similarity.bm25 import BM25
from module.report_similarity.deduplication import Deduplication
from module.report_similarity.lemmatization import Lemmatization


def _remove_emails(text: str) -> str:
    """Убрать адреса электронных почт."""
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    return re.sub(email_pattern, '', text)


def _remove_useless_words(text: str) -> str:
    """Убрать ненужные фразы."""
    for rplc in REPLACE_STMTS:
        text = text.replace(rplc, '')
    text = _remove_emails(text)
    return text


def clean_text(original_text: str):
    """Очистка текста от ненужных фраз/слов/предложений."""
    pure_text = _remove_emails(original_text)
    pure_text = _remove_useless_words(pure_text)
    return pure_text


class Pipeline:
    """Класс с пайплайном по обработке отчетов для нахождения похожих."""

    MAX_DIFF_DATE: ClassVar[int] = 3
    MAX_LENGTH: ClassVar[int] = 2_100
    MIN_BM25_SCORE: ClassVar[int] = 120
    USE_COLS: ClassVar[list[str]] = ['text', 'publication_date', 'report_id']
    USE_COLS_FROM_DB: ClassVar[list[str]] = USE_COLS + ['parent_report_id']

    def __init__(self):
        self.lemma_obj = Lemmatization()
        self.deduplicate_obj = Deduplication()

    async def _get_old_reports(self, min_date: dt.date, max_date: dt.date, new_reports_ids: list[str]) -> pd.DataFrame:
        """
        Получение старых отчетов из базы данных за определенный период.

        :param min_date:            Минимальная дата новых отчетов.
        :param max_date:            Максимальная дата новых отчетов.
        :param new_reports_ids:     Список report_id новых отчетов.
        :return:                    Датафрейм с отчетами из бд.
        """
        min_date_of_old_report = min_date - dt.timedelta(days=self.MAX_DIFF_DATE)
        max_date_of_old_report = max_date + dt.timedelta(days=self.MAX_DIFF_DATE)
        old_researches = await get_old_reports_for_period(min_date_of_old_report, max_date_of_old_report, new_reports_ids)
        if not old_researches:
            return pd.DataFrame()
        old_reports = [research_report.__dict__ for research_report in old_researches]
        return pd.DataFrame(old_reports)[self.USE_COLS_FROM_DB]

    def _find_small_in_big(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Нахождение вхождений маленьких отчетов в больших: проставление parent_report_id для вложенных отчетов.

        :param df:  Датафрейм с отчетами (после дедубликации).
        :return:    Датафрейм с выделением вложенных отчетов.
        """
        for report in df.itertuples():
            report: namedtuple

            if len(report.text) > self.MAX_LENGTH or report.parent_report_id:
                continue

            docs = df['text'].tolist()
            reports_ids = df['report_id'].tolist()
            publ_dates = df['publication_date'].tolist()
            docs.pop(report.Index)
            reports_ids.pop(report.Index)
            publ_dates.pop(report.Index)

            bm25 = BM25(docs)
            best_match_index, score = bm25.search(report.text)
            days_between_reports = abs(report.publication_date - publ_dates[best_match_index]).days
            if (
                    score > self.MIN_BM25_SCORE and  # балл схожести больше минимального
                    days_between_reports <= self.MAX_DIFF_DATE and  # разница между отчетами меньше N дней
                    len(docs[best_match_index]) > len(report.text)  # проверяемый отчет меньше найденного: входит в него
            ):
                df.loc[df['report_id'] == report.report_id, 'parent_report_id'] = reports_ids[best_match_index]
        return df

    async def find_similarity_reports(self, new_reports: list[dict[str, Any]]) -> None:
        """
        Нахождение дублей и вложенных отчетов, присвоение таким отчетам parent_report_id.

        :param new_reports: Словарь с атрибутами новых отчетов.
        """
        if not new_reports:
            return

        df = pd.DataFrame(new_reports)[self.USE_COLS]
        df['parent_report_id'] = None
        new_reports_ids = df['report_id'].tolist()
        df_from_db = await self._get_old_reports(min(df['publication_date']), max(df['publication_date']), new_reports_ids)
        df = pd.concat([df, df_from_db], ignore_index=True)

        df['clean_text'] = df['text'].apply(clean_text)
        df['lemma_text'] = df['clean_text'].apply(self.lemma_obj.lemma_text)

        df = self.deduplicate_obj.deduplicate_inner(df)
        df = self._find_small_in_big(df)
        children_parents_ids = dict(zip(df['report_id'], df['parent_report_id']))
        await update_parent_report_ids(children_parents_ids)
        # print(dict(filter(lambda item: item[1] is not None, children_parents_ids.items())))
