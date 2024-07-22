"""Модуль обработки новостей."""
import datetime as dt
import json
from typing import Iterable, Optional
from urllib.parse import unquote

import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from configs.config import psql_engine
from log.logger_base import Logger
from module.model_pipe import (
    add_text_sum_column,
    deduplicate,
    gigachat_filtering,
    model_func_online,
)


class ArticleProcess:
    """Класс обработчик новостей"""

    def __init__(self, logger: Logger.logger):
        """
        Инициализация объекта обработчика новостей.

        :param logger: Объект логгера.
        """
        self._logger = logger
        self.engine = create_engine(psql_engine, poolclass=NullPool)
        self.df_article = pd.DataFrame()  # original dataframe with data about article

    def clear_from_duplicates(self, df: pd.DataFrame, links_value: Optional[tuple[str]] = None) -> pd.DataFrame:
        """
        Очистить поступившие новости от уже содержащихся в базе данных.

        :param df:          Датафрейм с атрибутами новостей.
        :param links_value: Кортеж из ссылок на новости.
        :return:            Датафрейм без старых новостей.
        """
        if links_value is None:
            links_value = tuple(df['link'].apply(unquote))

        if not links_value:
            return df

        query_old_article = text('SELECT link FROM article WHERE link IN :links_value')
        with self.engine.connect() as conn:
            links_of_old_article = conn.execute(
                query_old_article.bindparams(links_value=links_value)).scalars().all()

        if links_of_old_article:
            df = df[~df['link'].isin(links_of_old_article)]
            self._logger.warning(
                f'В выгрузке содержатся старые новости! Количество новостей после их удаления - {len(df)}')
        return df

    def preprocess_article_online(self, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
        """
        Предобработать поступившие новости.

        :param df:  Датафрейм с новостями от GigaParsers.
        :return:    Обработанный датафрейм с поступившими новостями и id этих новостей.
        """
        new_name_columns = {'url': 'link', 'title': 'title', 'created_at': 'date', 'content': 'text'}
        columns = ['link', 'title', 'date', 'text']
        source_filter = ['The Economist']
        not_finish_article_filter = 'новость дополняется'

        df = df.rename(columns=new_name_columns)

        df = df[~df['source'].isin(source_filter)]
        self._logger.info(f'Удаление иностранных ресурсов, количество новостей - {len(df)}')

        df = df.dropna(subset='text')
        self._logger.info(f'Удаление новостей с пустым текстом, количество новостей - {len(df)}')

        df = df[~df['text'].str.contains(not_finish_article_filter, case=False)]
        self._logger.info(f'Удаление незаконченных новостей, количество новостей - {len(df)}')

        gotten_ids = dict(id=df['id'].values.tolist())
        gotten_ids = json.dumps(gotten_ids)
        df = df[columns]

        df['text'] = df['text'].str.replace('«', '"')
        df['text'] = df['text'].str.replace('»', '"')
        df['title'] = df['title'].str.replace('«', '"')
        df['title'] = df['title'].str.replace('»', '"')
        df['date'] = df['date'].apply(lambda x: pd.to_datetime(x, unit='s') + pd.to_timedelta(3, unit='h'))
        try:
            df = (
                df.groupby('link')
                .apply(lambda x: pd.Series(
                    {'title': x['title'].iloc[0], 'date': x['date'].iloc[0], 'text': x['text'].iloc[0]}
                ))
                .reset_index()
            )

            df = self.clear_from_duplicates(df)
            self._logger.info(f'Объединение новостей по одинаковым ссылкам, количество новостей - {len(df)}')
        except Exception as e:
            self._logger.error('Ошибка при объединении ссылок: %s', e)

        return df, gotten_ids

    def get_tg_articles(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Вынимает новости, которые связаны с тг-каналами, добавляет колонку с telegram_id.

        :param df:  DataFrame с предобработанными данными новостей (link, title, date, text, [id]).
        :return:    DataFrame с новостями только из списка телеграмм каналов (link, title, date, text, id, telegram_id).
        """
        query = 'SELECT id, link FROM telegram_channel;'
        tg_channels_df = pd.read_sql(query, con=self.engine)
        # Очищаем ссылки от / в конце
        tg_channels_df['link'] = tg_channels_df['link'].str.rstrip('/')

        if 'id' not in df.columns:
            df = df.assign(id=None)

        # save only tg news
        df_tg_news = (
            df.assign(telegram_link=df['link'].str.rsplit('/', n=1).str[0])
              .merge(tg_channels_df, left_on='telegram_link', right_on='link', suffixes=('', '_y'))
              .drop(['telegram_link', 'link_y'], axis=1)
        )

        # rename column 'id' from tg_channels_df to 'telegram_id'
        return df_tg_news.rename(columns={'id_y': 'telegram_id'})

    @staticmethod
    def update_tg_articles(saved_tg_articles: pd.DataFrame, all_tg_articles: pd.DataFrame) -> pd.DataFrame:
        """
        Соединение DataFrame сохраненных тг-новостей со всеми тг-новостями.

        :param saved_tg_articles:   DataFrame[['id', 'link', 'title', 'date', 'text', 'telegram_id']]
        :param all_tg_articles:     DataFrame[['id', 'link', 'title', 'date', 'text', 'telegram_id']]
        :return:                    DataFrame[['id', 'link', 'title', 'date', 'text', 'telegram_id']]
        """
        saved_tg_articles = saved_tg_articles[['id', 'link', 'title', 'date', 'text', 'telegram_id']]
        all_tg_articles = all_tg_articles[['id', 'link', 'title', 'date', 'text', 'telegram_id']]
        return pd.concat([saved_tg_articles, all_tg_articles]).drop_duplicates('link').reset_index()

    def throw_the_models(self, df: pd.DataFrame) -> pd.DataFrame:
        """Обработать датафрейм с помощью моделей."""
        return model_func_online(self._logger, df)

    def drop_duplicate(self) -> None:
        """Удалить дубли между поступившими новостями и новостями из базы данных."""
        dt_now = dt.datetime.now()
        old_query = (
            f'SELECT a.id, a.date,'
            f"STRING_AGG(DISTINCT client.name, ';') AS client, "
            f"STRING_AGG(DISTINCT commodity.name, ';') AS commodity, "
            f'ani.cleaned_data '
            f'FROM article a '
            f'LEFT JOIN relation_client_article r_client ON a.id = r_client.article_id '
            f'LEFT JOIN client ON r_client.client_id = client.id '
            f'LEFT JOIN relation_commodity_article r_commodity ON a.id = r_commodity.article_id '
            f'LEFT JOIN commodity ON r_commodity.commodity_id = commodity.id '
            f'JOIN article_name_impact ani ON ani.article_id = a.id '
            f"WHERE '{dt_now}' - a.date < '15 day' "
            f'GROUP BY a.id, a.date, ani.cleaned_data'
        )
        old_articles = pd.read_sql(old_query, con=self.engine)
        # заполняем нулями пустые значения, чтобы разделить новости на релевантные и нерелевантные
        self.df_article['client_score'] = self.df_article['client_score'].fillna(0)
        self.df_article['commodity_score'] = self.df_article['commodity_score'].fillna(0)
        # делим новости на релевантные и нерелевантные
        articles_relevant = self.df_article[(self.df_article['client_score'] > 0) | (self.df_article['commodity_score'] > 0)]
        articles_not_relevant = self.df_article[(self.df_article['client_score'] <= 0) & (self.df_article['commodity_score'] <= 0)]
        # отдельно их дедублицируем
        articles_relevant = deduplicate(self._logger, articles_relevant, old_articles)
        articles_not_relevant = deduplicate(self._logger, articles_not_relevant, old_articles)
        # соединяем обратно в один батч
        self.df_article = pd.concat([articles_relevant, articles_not_relevant], ignore_index=True)

    def make_text_sum(self) -> None:
        """Вызвать функцию по суммаризации новостей."""
        self.df_article = add_text_sum_column(self._logger, self.df_article)

    def apply_gigachat_filtering(self) -> None:
        """Применяем фильтрацию новостей с помощью gigachat"""
        self.df_article = gigachat_filtering(self._logger, self.df_article)

    @staticmethod
    def clean_data_from_html_tags(html_content: str | None) -> str:
        """
        Очистить данные от html тегов.

        Позволяет очистить данные от незакрытых html тегов.

        :param html_content: Данные, которые требуется очистить от html тегов.
        :return: Очищенные данные
        """
        return BeautifulSoup(html_content, 'html.parser').get_text() if html_content else ''

    def remove_html_tags(self, columns_to_clear: Iterable[str] = ('title', 'text', 'text_sum')) -> None:
        """
        Очистить данные self.df_article от html тегов.

        :param columns_to_clear: Список имен столбцов, для которых требуется провести очистку данных от html тегов.
        """
        for col in columns_to_clear:
            self.df_article[col].apply(self.clean_data_from_html_tags)

    def save_tables(self) -> list[str]:
        """
        Сохранить новости, получить id сохраненных новостей из бд, вызвать методы по сохранению таблиц отношений.

        :return: Список ссылок сохраненных новостей.
        """
        links_value = tuple(self.df_article['link'].apply(unquote))
        if not links_value:
            return []

        self.df_article = self.clear_from_duplicates(self.df_article, links_value)

        # make article table and save it in database
        article = self.df_article[['link', 'title', 'date', 'text', 'text_sum']]
        article.to_sql('article', con=self.engine, if_exists='append', index=False)
        self._logger.info(f'Сохранено {len(article)} новостей')

        # add ids to df_article from article table from db
        query_ids = text('SELECT id, link FROM article WHERE link IN :links_value')
        with self.engine.connect() as conn:
            ids_data = conn.execute(query_ids.bindparams(links_value=links_value)).all()
            ids = pd.DataFrame(ids_data, columns=['id', 'link'])

        # merge ids from db with df_article
        self.df_article = self.df_article.merge(pd.DataFrame(ids), on='link')

        # save data in article_impact table
        article_name_impact = self.df_article[['id', 'cleaned_data', 'client_impact', 'commodity_impact']].rename(
            columns={'id': 'article_id'}
        )
        article_name_impact.to_sql('article_name_impact', con=self.engine, if_exists='append', index=False)
        self._logger.debug('Сохранены вхождения объектов')

        # make relation tables between articles and client and commodity
        self._make_save_relation_article_table('client')
        self._make_save_relation_article_table('commodity')

        return self.df_article['link'].values.tolist()

    def _make_save_relation_article_table(self, name: str) -> None:
        """
        Создать таблицы отношений и сохранить их в базу данных.

        :param name: Объект (клиент или коммод).
        """
        subject = pd.read_sql(f'SELECT * FROM {name}', con=self.engine).rename(columns={'id': f'{name}_id', 'name': name})
        # make in-between df about article id and client data
        df_article_subject = self.df_article.dropna(subset=name)[['id', name, f'{name}_score']]
        df_article_subject.rename(columns={'id': 'article_id'}, inplace=True)

        #  if many client in one cell
        df_article_subject[name] = df_article_subject[name].str.split(';')
        df_article_subject = df_article_subject.explode(name)

        # make relation df between client id and article id
        df_relation_subject_article = df_article_subject.merge(subject, on=name)[[f'{name}_id', 'article_id', f'{name}_score']]
        # save relation df to database
        df_relation_subject_article.to_sql(f'relation_{name}_article', con=self.engine, if_exists='append', index=False)
        self._logger.info(f'В таблицу relation_{name}_article добавлено {len(df_relation_subject_article)} строк')

    def save_tg_tables(self) -> list:
        """
        Сохраняет self.df_article, как новости из тг-каналов, связывая их с тг-каналами.

        return: список ссылок сохраненных новостей
        """
        subject = 'telegram'
        links_value = ', '.join([f"'{unquote(link)}'" for link in self.df_article['link'].values.tolist()])
        # make article table and save it in database
        unsaved_article = self.df_article[self.df_article['id'].isnull()]

        unsaved_article = self.clear_from_duplicates(unsaved_article)

        article = unsaved_article[['link', 'title', 'date', 'text', 'text_sum']]
        article.to_sql('article', con=self.engine, if_exists='append', index=False)
        self._logger.info(f'Сохранено {subject} {len(article)} новостей')

        # add ids to df_article from article table from db
        query_ids = f'SELECT id, link FROM article WHERE link IN ({links_value})'
        ids = pd.read_sql(query_ids, con=self.engine)

        # merge ids from db with df_article
        self.df_article = self.df_article.drop(columns=['id']).merge(pd.DataFrame(ids), on='link').drop_duplicates('link')

        # make relation tables between articles and telegram
        df_article_subject = self.df_article[['id', f'{subject}_id']]
        df_article_subject.rename(columns={'id': 'article_id'}, inplace=True)
        df_article_subject[f'{subject}_score'] = 0

        tmp_table = f'temporary_relation_{subject}_article'
        df_article_subject.to_sql(tmp_table, con=self.engine, if_exists='append', index=False)

        with self.engine.begin() as conn:
            sql = text(
                f'INSERT INTO relation_{subject}_article ({subject}_id, article_id, {subject}_score) '
                f'SELECT t.{subject}_id, t.article_id, t.{subject}_score '
                f'FROM {tmp_table} t '
                f'   WHERE NOT EXISTS '
                f'      (SELECT 1 FROM relation_{subject}_article f '
                f'       WHERE t.{subject}_id = f.{subject}_id '
                f'       AND t.article_id = f.article_id)'
            )
            delete_tmp_table_sql = text(f'DROP TABLE IF EXISTS {tmp_table}')

            conn.execute(sql)
            conn.execute(delete_tmp_table_sql)
            # На всякий случай пусть будет, хоть дроп таблицы и триггерит коммит
            conn.commit()

        return article['link'].values.tolist()
