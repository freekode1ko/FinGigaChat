import pandas as pd

from constants import constants
from log.logger_base import Logger


class Transformer:
    def __init__(self, logger: Logger.logger):
        self._logger = logger
        self.tables_handbook = constants.TABLES_HANDBOOK

    @staticmethod
    def filter_list(lst: list) -> list:
        """
        Форматирование колонок для DataFrame. Убирает первые 'Unnamed: N' колонки оставляя с наибольшей N

        :param lst: List[] или numpy.ndarray с наименованиями колонок
        """
        for i in range(len(lst)):
            if lst[i].isdigit():
                return lst[i - 1:]
        return lst

    def process_fin_summary_table(self, page_html: str, company_id: int, metadata_df: pd.DataFrame) -> pd.DataFrame:
        """
        Обработка страницы сектора. Попытка вытащить из нее таблицы P&L (Прибыль и убытки), Баланс и Денежный поток

        :param page_html: HTML код страницы
        :param company_id: id компании(клиента) на research
        :param metadata_df: DataFrame содержащий в себе основные данные по отчетам. [id сектора на research,
        id клиента на research, id клиента в нашей БД, отчет PL, балансовый отчет, отчет денежных движений]
        """
        ecom_tables = pd.read_html(page_html, decimal=',', thousands='.')
        for table_num, table in enumerate(ecom_tables):
            if table_num in self.tables_handbook:
                cleaned_columns = self.filter_list(table.columns.values)  # очистка от ненужных колонок
                table = table[cleaned_columns].iloc[1:, :]  # отброс наименования таблицы
                table.rename(columns={cleaned_columns[0]: ''}, inplace=True)
                table[cleaned_columns[1:]] = table[cleaned_columns[1:]].replace('\.', ',', regex=True)
                # запись полученных таблиц в исходных df
                company_filter = metadata_df.company_id == company_id
                metadata_df.loc[company_filter, self.tables_handbook[table_num]] = [table.to_dict()]

        return metadata_df
