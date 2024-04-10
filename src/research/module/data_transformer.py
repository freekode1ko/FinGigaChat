from typing import List

import pandas as pd


class Transformer:
    @staticmethod
    def filter_list(lst: List[str]) -> List[str]:
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

        :param page_html:
        :param company_id:
        :param metadata_df: DataFrame содержащий в себе основные данные по отчетам. [id сектора на research,
        id клиента на research, id клиента в нашей БД, отчет PL, балансовый отчет, отчет денежных движений]
        """
        tables_handbook = {0: 'review_table', 1: 'pl_table', 2: 'balance_table', 3: 'money_table'}
        self._logger.info('Преобразуем таблицы из HTML в DF для поиска фин.показателей')
        ecom_tables = pd.read_html(page_html.text, decimal=',', thousands='.')
        for table_num, table in enumerate(ecom_tables):
            if table_num in [0, 1, 2, 3]:
                cleaned_columns = self.filter_list(table.columns.values)  # очистка от ненужных колонок
                table = table[cleaned_columns].iloc[1:, :]  # отброс наименования таблицы
                table.rename(columns={cleaned_columns[0]: ''}, inplace=True)
                table[cleaned_columns[1:]] = table[cleaned_columns[1:]].replace('\.', ',', regex=True)
                # запись полученных таблиц в исходных df
                company_filter = metadata_df.company_id == company_id
                metadata_df.loc[company_filter, tables_handbook[table_num]] = [table.to_dict()]

        return metadata_df
