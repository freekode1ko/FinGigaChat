import datetime as dt
import os
from urllib.parse import unquote

import pandas as pd
from sqlalchemy import text

from db.database import engine
from log.logger_base import Logger
from module.model_pipe import (
    add_text_sum_column,
    deduplicate,
    model_func,
    model_func_online,
)


class ArticleProcess:
    def __init__(self, logger: Logger.logger):
        self._logger = logger
        self.engine = engine
        self.df_article = pd.DataFrame()  # original dataframe with data about article

    @staticmethod
    def get_filename(dir_path):
        list_of_files = [filename for filename in os.listdir(dir_path)]
        filename = '' if not list_of_files else list_of_files[0]
        return filename

    def load_file(self, filepath: str, type_of_article: str) -> pd.DataFrame:
        """
        Load and process articles file.
        :param filepath: file path to Excel file with articles
        :param type_of_article: type of article (client or commodity)
        :return: dataframe of articles
        """
        source_filter = (
            '(www|realty|quote|pro|marketing).rbc.ru|.interfax(|-russia).ru|www.kommersant.ru|'
            'www.vedomosti.ru|//tass.(ru|com)/|(realty.|//)ria.ru|/1prime.ru/|www.banki.ru|'
            '(.|//)iz.ru/|//(|www.)ura.news|//(|www.)ru24.net|//(|www.)energyland.info|'
            'www.atomic-energy.ru|//(|www.)novostimira24.ru|//(|www.)eadaily.com|'
            '//(|www.)glavk.net|//(|www.)rg.ru|russian.rt.com|//(|www.)akm.ru|//(|www.)metaldaily.ru|'
            '//\w{0,10}(|.)aif.ru|//(|www.)nsn.fm|//(|www.)yamal-media.ru|//(|www.)life.ru|'
            '//(|www.)pronedra.ru|metallplace.ru|rzd-partner.ru|morvesti.ru|morport.com|gudok.ru|'
            'eprussia.ru|metallicheckiy-portal.ru|gmk.center|bigpowernews.ru|metaltorg.ru|new-retail.ru|'
            'agroinvestor.ru|comnews.ru|telecomdaily.ru|vestnik-sviazy.ru|neftegaz.ru|chemicalnews.ru|'
            'ru.tradingview.com|osnmedia.ru|forbes.ru|expert.ru|rupec.ru'
        )  # TODO: дополнять

        if type_of_article == 'client':
            new_name_columns = {
                'url': 'link',
                'title': 'title',
                'date': 'date',
                'New Topic Confidence': 'coef',
                'text': 'text',
                'text Summary Summary': 'text_sum',
                'Company_name': 'client',
            }
            columns = ['link', 'title', 'date', 'text', 'client']
        else:
            new_name_columns = {'url': 'link', 'title': 'title', 'date': 'date', 'text': 'text', 'Металл': 'commodity'}
            columns = ['link', 'title', 'date', 'text', 'commodity']

        df_subject = pd.read_csv(filepath, index_col=False).rename(columns=new_name_columns)
        df_subject = df_subject[columns]

        self._logger.info(f'Получено {len(df_subject)} {type_of_article} новостей')
        df_subject = df_subject[~df_subject['link'].str.contains(source_filter)]
        self._logger.info(f'Убраны некоторые источники, количество новостей - {len(df_subject)}')

        df_subject['text'] = df_subject['text'].str.replace('«', '"')
        df_subject['text'] = df_subject['text'].str.replace('»', '"')
        df_subject['text'] = df_subject['text'].str.replace('$', ' $')
        df_subject['date'] = df_subject['date'].apply(lambda x: dt.datetime.strptime(x, '%m/%d/%Y %H:%M:%S %p'))
        df_subject['title'] = df_subject['title'].apply(lambda x: None if x == '0' else x)
        df_subject['title'] = df_subject['title'].apply(lambda x: x.replace('$', ' $') if isinstance(x, str) else x)
        df_subject[type_of_article] = df_subject[type_of_article].str.lower()
        try:
            df_subject = (
                df_subject.groupby('link')
                .apply(
                    lambda x: pd.Series(
                        {
                            'title': x['title'].iloc[0],
                            'date': x['date'].iloc[0],
                            'text': x['text'].iloc[0],
                            type_of_article: ';'.join(x[type_of_article]),
                        }
                    )
                )
                .reset_index()
            )
            self._logger.info(f'Объединение новостей по одинаковым ссылкам, количество новостей - {len(df_subject)}')
        except Exception as e:
            self._logger.error('Ошибка при объединении ссылок: %s', e)

        return df_subject

    def throw_the_models(self, df: pd.DataFrame, name: str = '', online_flag: bool = True) -> pd.DataFrame:
        """Call model pipe func"""
        df = model_func_online(self._logger, df) if online_flag else model_func(self._logger, df, name)
        return df

    def drop_duplicate(self):
        """Call func to delete similar articles"""
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

    def make_text_sum(self):
        """Call summary func"""
        self.df_article = add_text_sum_column(self._logger, self.df_article)

    def merge_client_commodity_article(self, df_client: pd.DataFrame, df_commodity: pd.DataFrame):
        """
        Merge df of client and commodity and drop duplicates
        And set it in self.df_article.
        :param df_client: df with client article
        :param df_commodity: df with commodity article
        """
        # find common link in client and commodity article, and take client from these article
        df_link_client = df_client[['link', 'client', 'client_impact', 'client_score']][df_client['link'].isin(df_commodity['link'])]
        # make df bases on common links, which contains client and commodity name
        df_client_commodity = df_commodity.merge(df_link_client, on='link')
        # remove from df_client and df_commodity common links
        df_commodity = df_commodity[~df_commodity['link'].isin(df_link_client['link'])]
        df_client = df_client[~df_client['link'].isin(df_link_client['link'])]
        # concat all df in one, so there are no duplicates and contain all data
        df_article = pd.concat([df_client, df_commodity, df_client_commodity], ignore_index=True)
        self.df_article = df_article[
            [
                'link',
                'title',
                'date',
                'text',
                'client',
                'commodity',
                'client_impact',
                'commodity_impact',
                'client_score',
                'commodity_score',
                'cleaned_data',
            ]
        ]
        self._logger.info(f'Количество одинаковых новостей в выгрузках по клиентам и товарам - {len(df_client_commodity)}')
        self._logger.info(f'Количество новостей после объединения выгрузок - {len(df_article)}')

    def save_tables(self) -> list:
        """
        Сохраняет новости, получает id сохраненных новостей из бд,
        вызывает методы по сохранению таблиц отношений
        return: список ссылок сохраненных новостей
        """

        links_value = tuple(self.df_article['link'].apply(unquote))
        if not links_value:
            return []

        query_old_article = text('SELECT link FROM article WHERE link IN :links_value')
        with self.engine.connect() as conn:
            links_of_old_article = conn.execute(query_old_article.bindparams(links_value=links_value)).scalars().all()

        if links_of_old_article:
            self.df_article = self.df_article[~self.df_article['link'].isin(links_of_old_article)]
            self._logger.warning(
                f'В выгрузке содержатся старые новости! Количество новостей после их удаления - {len(self.df_article)}')

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
        Make relation table and save it to database.
        :param name: name (client or commodity)
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
