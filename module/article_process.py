import os
import datetime as dt
import numpy as np
import json
from urllib.parse import unquote, urlparse
from typing import List, Dict, Union

import pandas as pd
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

from config import psql_engine, NEWS_LIMIT
from module.model_pipe import deduplicate, model_func, model_func_online, add_text_sum_column
from module.logger_base import Logger


TIME_LIVE_ARTICLE = 100
NOT_RELEVANT_EXPRESSION = ['читайте также', 'беспилотник', 'смотрите']
CONDITION_TOP = ("{condition_word} CURRENT_DATE - {table}.date < '15 day' AND "
                 "({table}.link SIMILAR TO '%(www|realty|quote|pro|marketing).rbc%' "
                 "OR {table}.link SIMILAR TO '%.interfax(|-russia).ru%' "
                 "OR {table}.link SIMILAR TO '%www.kommersant.ru%' "
                 "OR {table}.link SIMILAR TO '%www.vedomosti.ru%' "
                 "OR {table}.link SIMILAR TO '%www.forbes.ru%' "
                 "OR {table}.link SIMILAR TO '%(.|//)iz.ru/%' "
                 "OR {table}.link SIMILAR TO '%//tass.(ru|com)%' "
                 "OR {table}.link SIMILAR TO '%(realty.|//)ria.ru%')")


class ArticleProcess:
    def __init__(self, logger: Logger.logger):
        self._logger = logger
        self.engine = create_engine(psql_engine, poolclass=NullPool)
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
        source_filter = ("(www|realty|quote|pro|marketing).rbc.ru|.interfax(|-russia).ru|www.kommersant.ru|"
                         "www.vedomosti.ru|//tass.(ru|com)/|(realty.|//)ria.ru|/1prime.ru/|www.banki.ru|"
                         "(.|//)iz.ru/|//(|www.)ura.news|//(|www.)ru24.net|//(|www.)energyland.info|"
                         "www.atomic-energy.ru|//(|www.)novostimira24.ru|//(|www.)eadaily.com|"
                         "//(|www.)glavk.net|//(|www.)rg.ru|russian.rt.com|//(|www.)akm.ru|//(|www.)metaldaily.ru|"
                         "//\w{0,10}(|.)aif.ru|//(|www.)nsn.fm|//(|www.)yamal-media.ru|//(|www.)life.ru|"
                         "//(|www.)pronedra.ru|metallplace.ru|rzd-partner.ru|morvesti.ru|morport.com|gudok.ru|"
                         "eprussia.ru|metallicheckiy-portal.ru|gmk.center|bigpowernews.ru|metaltorg.ru|new-retail.ru|"
                         "agroinvestor.ru|comnews.ru|telecomdaily.ru|vestnik-sviazy.ru|neftegaz.ru|chemicalnews.ru|"
                         "ru.tradingview.com|osnmedia.ru|forbes.ru|expert.ru|rupec.ru")  # TODO: дополнять

        if type_of_article == 'client':
            new_name_columns = {'url': 'link', 'title': 'title', 'date': 'date', 'New Topic Confidence': 'coef',
                                'text': 'text', 'text Summary Summary': 'text_sum', 'Company_name': 'client'}
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
            df_subject = df_subject.groupby('link').apply(lambda x: pd.Series({
                'title': x['title'].iloc[0],
                'date': x['date'].iloc[0],
                'text': x['text'].iloc[0],
                type_of_article: ';'.join(x[type_of_article]),
            })).reset_index()
            self._logger.info(f'Объединение новостей по одинаковым ссылкам, количество новостей - {len(df_subject)}')
        except Exception as e:
            self._logger.error(f'Ошибка при объединении ссылок: {e}')

        return df_subject

    def preprocess_article_online(self, df: pd.DataFrame):
        """
        Preprocess articles dataframe and set df.
        :param df: df with articles
        :return: dataframe of articles
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
            df = df.groupby('link').apply(lambda x: pd.Series({'title': x['title'].iloc[0], 'date': x['date'].iloc[0],
                                                               'text': x['text'].iloc[0]})).reset_index()
            self._logger.info(f'Объединение новостей по одинаковым ссылкам, количество новостей - {len(df)}')
        except Exception as e:
            self._logger.error(f'Ошибка при объединении ссылок: {e}')

        return df, gotten_ids

    def throw_the_models(self, df: pd.DataFrame, name: str = '', online_flag: bool = True) -> pd.DataFrame:
        """ Call model pipe func """
        df = model_func_online(self._logger, df) if online_flag else model_func(self._logger, df, name)
        return df

    def drop_duplicate(self):
        """ Call func to delete similar articles """
        dt_now = dt.datetime.now()
        old_query = (f"SELECT a.id, "
                     f"STRING_AGG(DISTINCT client.name, ';') AS client, "
                     f"STRING_AGG(DISTINCT commodity.name, ';') AS commodity, "
                     f"ani.cleaned_data "
                     f"FROM article a "
                     f"LEFT JOIN relation_client_article r_client ON a.id = r_client.article_id "
                     f"LEFT JOIN client ON r_client.client_id = client.id "
                     f"LEFT JOIN relation_commodity_article r_commodity ON a.id = r_commodity.article_id "
                     f"LEFT JOIN commodity ON r_commodity.commodity_id = commodity.id "
                     f"JOIN article_name_impact ani ON ani.article_id = a.id "
                     f"WHERE '{dt_now}' - a.date < '15 day' "
                     f"GROUP BY a.id, ani.cleaned_data")
        old_articles = pd.read_sql(old_query, con=self.engine)
        self.df_article = deduplicate(self._logger, self.df_article, old_articles)

    def make_text_sum(self):
        """ Call summary func """
        self.df_article = add_text_sum_column(self._logger, self.df_article)

    def delete_old_article(self):
        """ Delete from db article if there are 10 articles for each subject """
        count_to_keep = 30
        query_delete = (f"delete from article where id not in ( "
                        f"select distinct article_id from "
                        f"(select *, row_number() over(partition by client_id order by a.date desc, client_score desc) rn "
                        f"from relation_client_article r "
                        f"join article a on r.article_id = a.id) t1 "
                        f"where rn <= {count_to_keep} and t1.client_score > 0"
                        f"UNION "
                        f"select distinct article_id from "
                        f"(select *, row_number() over(partition by commodity_id order by a.date desc, commodity_score desc) rn "
                        f"from relation_commodity_article r "
                        f"join article a on r.article_id = a.id) t1 "
                        f"where rn <= {count_to_keep} and t1.commodity_score > 0)")
        with self.engine.connect() as conn:
            len_before = conn.execute(text("SELECT COUNT(id) FROM article")).fetchone()
            conn.execute(text(query_delete))
            conn.commit()
            len_after = conn.execute(text("SELECT COUNT(id) FROM article")).fetchone()
            self._logger.info(f'Удалено {len_before[0] - len_after[0]} новостей')
            dt_now = dt.datetime.now()
            conn.execute(text(f"DELETE FROM article WHERE '{dt_now}' - date > '{TIME_LIVE_ARTICLE} day'"))
            conn.commit()
            len_finish = conn.execute(text("SELECT COUNT(id) FROM article")).fetchone()
            self._logger.info(f'Удалено {len_after[0] - len_finish[0]} новостей с датой публикации больше 100 дней назад')

    def merge_client_commodity_article(self, df_client: pd.DataFrame, df_commodity: pd.DataFrame):
        """
        Merge df of client and commodity and drop duplicates
        And set it in self.df_article.
        :param df_client: df with client article
        :param df_commodity: df with commodity article
        """
        # find common link in client and commodity article, and take client from these article
        df_link_client = df_client[['link', 'client', 'client_impact', 'client_score']][
            df_client['link'].isin(df_commodity['link'])]
        # make df bases on common links, which contains client and commodity name
        df_client_commodity = df_commodity.merge(df_link_client, on='link')
        # remove from df_client and df_commodity common links
        df_commodity = df_commodity[~df_commodity['link'].isin(df_link_client['link'])]
        df_client = df_client[~df_client['link'].isin(df_link_client['link'])]
        # concat all df in one, so there are no duplicates and contain all data
        df_article = pd.concat([df_client, df_commodity, df_client_commodity], ignore_index=True)
        self.df_article = df_article[['link', 'title', 'date', 'text', 'client', 'commodity', 'client_impact',
                                      'commodity_impact', 'client_score', 'commodity_score', 'cleaned_data']]
        self._logger.info(f'Количество одинаковых новостей в выгрузках по клиентам и товарам - {len(df_client_commodity)}')
        self._logger.info(f'Количество новостей после объединения выгрузок - {len(df_article)}')

    def save_tables(self) -> None:
        """
        Save article, get ids for original df from db,
        And call make_save method for relation table.
        """
        # TODO: оставляет 8 дублирующих новостей
        # filter dubl news if they in DB and in new df
        links_value = ", ".join([f"'{unquote(link)}'" for link in self.df_article["link"].values.tolist()])
        query_old_article = f'SELECT link FROM article WHERE link IN ({links_value})'
        links_of_old_article = pd.read_sql(query_old_article, con=self.engine)
        if not links_of_old_article.empty:
            self.df_article = self.df_article[~self.df_article['link'].isin(links_of_old_article.link)]
            self._logger.warning(f'В выгрузке содержатся старые новости! Количество новостей после их удаления - '
                                 f'{len(self.df_article)}')

        # make article table and save it in database
        article = self.df_article[['link', 'title', 'date', 'text', 'text_sum']]
        article.to_sql('article', con=self.engine, if_exists='append', index=False)
        self._logger.info(f'Сохранено {len(article)} новостей')

        # add ids to df_article from article table from db
        query_ids = f"SELECT id, link FROM article WHERE link IN ({links_value})"
        ids = pd.read_sql(query_ids, con=self.engine)

        # merge ids from db with df_article
        self.df_article = self.df_article.merge(pd.DataFrame(ids), on='link')

        # save data in article_impact table
        article_name_impact = self.df_article[['id', 'cleaned_data', 'client_impact', 'commodity_impact']].rename(
            columns={'id': 'article_id'})
        article_name_impact.to_sql('article_name_impact', con=self.engine, if_exists='append', index=False)
        self._logger.debug('Сохранены вхождения объектов')

        # make relation tables between articles and client and commodity
        self._make_save_relation_article_table('client')
        self._make_save_relation_article_table('commodity')

    def _make_save_relation_article_table(self, name: str) -> None:
        """
        Make relation table and save it to database.
        :param name: name (client or commodity)
        """
        subject = pd.read_sql(f'SELECT * FROM {name}', con=self.engine).rename(columns={'id': f'{name}_id',
                                                                                        'name': name})
        # make in-between df about article id and client data
        df_article_subject = self.df_article.dropna(subset=name)[['id', name, f'{name}_score']]
        df_article_subject.rename(columns={'id': 'article_id'}, inplace=True)

        #  if many client in one cell
        df_article_subject[name] = df_article_subject[name].str.split(';')
        df_article_subject = df_article_subject.explode(name)

        # make relation df between client id and article id
        df_relation_subject_article = df_article_subject.merge(subject, on=name)[[f'{name}_id', 'article_id',
                                                                                  f'{name}_score']]
        # save relation df to database
        df_relation_subject_article.to_sql(f'relation_{name}_article', con=self.engine, if_exists='append', index=False)
        self._logger.info(f'В таблицу relation_{name}_article добавлено {len(df_relation_subject_article)} строк')

    def find_subject_id(self, message: str, subject: str):
        """
        Find id of client or commodity by user message
        :param message: user massage
        :param subject: client or commodity
        :return: id of client(commodity) or False if user message not about client or commodity
        """
        subject_ids = []
        message_text = message.lower().strip().replace('"', '')
        df_alternative = pd.read_sql(f'SELECT {subject}_id, other_names FROM {subject}_alternative', con=self.engine)
        df_alternative['other_names'] = df_alternative['other_names'].apply(lambda x: x.split(';'))
        for subject_id, names in zip(df_alternative[f'{subject}_id'], df_alternative['other_names']):
            if message_text in names:
                subject_ids.append(subject_id)
        return subject_ids

    def _get_articles(self, subject_id: int, subject: str, limit_all: int = NEWS_LIMIT, offset_all: int = 0):
        """
        Get sorted sum article by subject id.
        :param subject_id: id of client or commodity
        :param subject: client or commodity
        :return: name of client(commodity) and sorted sum articles
        """
        count_all, count_top = limit_all, 3
        offset_top = 0
        query_temp = ('SELECT relation.article_id, relation.{subject}_score, '
                      'article_.title, article_.date, article_.link, article_.text_sum '
                      'FROM relation_{subject}_article AS relation '
                      'INNER JOIN ('
                      'SELECT id, title, date, link, text_sum '
                      'FROM article '
                      ') AS article_ '
                      'ON article_.id = relation.article_id '
                      'WHERE relation.{subject}_id = {subject_id} AND relation.{subject}_score > 0 '
                      '{condition} '
                      'ORDER BY date DESC, relation.{subject}_score DESC '
                      'OFFSET {offset} '
                      'LIMIT {count}')
        condition_top = CONDITION_TOP.format(condition_word='AND', table='article_')

        with self.engine.connect() as conn:

            query_article_top_data = query_temp.format(subject=subject, subject_id=subject_id,
                                                       count=count_top, condition=condition_top,
                                                       offset=offset_top)
            result_top = conn.execute(text(query_article_top_data)).fetchall()
            article_data_top = [item[2:] for item in result_top]
            article_data_top_len = len(article_data_top)
            top_link = ','.join([f"'{item[4]}'" for item in result_top]) if result_top else "''"

            offset_all_updated = ((offset_all - article_data_top_len) if offset_all > article_data_top_len else 0)

            condition_all = f"AND article_.link not in ({top_link})"
            query_article_all_data = query_temp.format(subject=subject, subject_id=subject_id,
                                                       count=count_all, condition=condition_all,
                                                       offset=offset_all_updated)

            article_data_all = [item[2:] for item in conn.execute(text(query_article_all_data))]
            count_of_not_top_news = count_all - len(article_data_top)
            article_data = article_data_top + article_data_all[:count_of_not_top_news] if not offset_all else article_data_all

            name = conn.execute(text(f'SELECT name FROM {subject} WHERE id={subject_id}')).fetchone()[0]

            return name, article_data

    def _get_sorted_subject(self) -> (Dict, Dict):
        """ Создание словарей для сортировки по топ клиентам/товарам
        в зависимости от кол-ва новостей за период времени """
        period = '3 months'
        query_sort = ("select name from {subject_type} "
                      "join relation_{subject_type}_article r_{subject_type} "
                      "on r_{subject_type}.{subject_type}_id = {subject_type}.id "
                      "join article on article.id=r_{subject_type}.article_id "
                      "where current_date - article.date < '{period}' "
                      "group by name order by count(r_{subject_type}.article_id) desc")
        with self.engine.connect() as conn:
            client_sorted = conn.execute(text(query_sort.format(subject_type='client', period=period))).fetchall()
            commodity_sorted = conn.execute(text(query_sort.format(subject_type='commodity', period=period))).fetchall()

        # словарь с именем объекта и его индексом
        client_sorted_dict = {key[0]: val for key, val in zip(list(client_sorted), range(len(client_sorted)))}
        commodity_sorted_dict = {key[0]: val for key, val in zip(list(commodity_sorted), range(len(commodity_sorted)))}

        return client_sorted_dict, commodity_sorted_dict

    @staticmethod
    def _sort_by_top_subject(sorted_subject_name: Dict, articles) -> List:
        """
        Возвращает отсортированный по топ объектам список со статьями
        :param sorted_subject_name: словарь {имя объекта: отсортированный индекс}
        :param articles: данные по новостям, включая имена объектов
        """
        last_place = 1000000
        article_sorted_dict = {}
        for article in articles:
            subject_name = article[1]
            sorted_place = sorted_subject_name.get(subject_name, last_place)
            article_sorted_dict[article] = sorted_place

        article_sorted = sorted(article_sorted_dict.items(), key=lambda item: item[1])  # кортеж (ключ, значение)
        article_sorted = [a[0] for a in article_sorted]  # список из ключей, т.е. только из данных по новостям
        return article_sorted

    def _get_industry_articles(self, industry_id) -> List:
        """ Получение отсортированных новостей по клиентам и товарам для выдачи новостей по отрасли """
        query = ("SELECT * FROM "
                 "(SELECT industry.name, {subject}.name, article.date, article.link, article.title, article.text_sum, "
                 "ROW_NUMBER() OVER(PARTITION BY {subject}.name ORDER BY "
                 "CASE {condition} THEN 1 "
                 "END, "
                 "article.date desc, r.{subject}_score desc) rn "
                 "FROM relation_{subject}_article r "
                 "JOIN article ON r.article_id=article.id "
                 "JOIN {subject} ON {subject}.id=r.{subject}_id "
                 "JOIN industry ON industry.id={subject}.industry_id "
                 "WHERE industry.id={industry_id} AND r.{subject}_score > 0 ) t1 "
                 "WHERE rn<=2 and CURRENT_DATE - date < '8 day' ")

        condition = CONDITION_TOP.format(condition_word='WHEN', table='article')
        q_client = query.format(subject='client', industry_id=industry_id, condition=condition)
        q_commodity = query.format(subject='commodity', industry_id=industry_id, condition=condition)
        with self.engine.connect() as conn:
            articles_client = conn.execute(text(q_client)).fetchall()
            articles_commodity = conn.execute(text(q_commodity)).fetchall()

        # получим словарь с отсортированными по кол-ву новостей за квартал клиентами/товарами
        client_sorted_dict, commodity_sorted_dict = self._get_sorted_subject()
        # отсортируем полученные статьи по топ клиентам/товарам
        client_sorted = self._sort_by_top_subject(client_sorted_dict, articles_client)
        commodity_sorted = self._sort_by_top_subject(commodity_sorted_dict, articles_commodity)

        articles = list(client_sorted) + list(commodity_sorted)

        return articles

    def _get_commodity_pricing(self, subject_id):
        """
        Get pricing about commodity from db.
        :param subject_id: id of commodity
        :return: list(dict) data about commodity pricing
        """

        pricing_keys = ('subname', 'unit', 'price', 'm_delta', 'y_delta', 'cons')

        with self.engine.connect() as conn:
            query_com_pricing = f'SELECT * FROM commodity_pricing WHERE commodity_id={subject_id}'
            com_data = conn.execute(text(query_com_pricing)).fetchall()
        all_commodity_data = [{key: value for key, value in zip(pricing_keys, com[2:])} for com in com_data]

        return all_commodity_data

    def get_client_fin_indicators(self, client_id, client_name):
        """
        Get company finanical indicators.
        :param client_id: id of company in client table
        :param client_name: str of company in user's message
        :return: df financial indicators
        """
        if client_id:
            client = pd.read_sql('client', con=self.engine)
            client_name = client[client['id'] == client_id]['name'].iloc[0]
        client = pd.read_sql('financial_indicators', con=self.engine)
        client = client[client['company'] == client_name]
        client = client.sort_values('id')
        client_copy = client.copy()

        if not client.empty:
            alias_idx = client.columns.get_loc('alias')
            new_df = client.iloc[:, :alias_idx]
            full_nan_cols = new_df.isna().all().sum()

            if full_nan_cols > 1:
                alias_idx = client_copy.columns.get_loc('alias')
                left_client = client_copy.iloc[:, :alias_idx]
                remaining_cols = 5 - left_client.notnull().sum(axis=1).iloc[0]
                right_client = client_copy.iloc[:, alias_idx:]
                selected_cols = left_client.columns[left_client.notnull().sum(axis=0) > 0][:5]

                if len(selected_cols) < 5:
                    if full_nan_cols < 5:
                        remaining_numeric_cols = list(right_client.select_dtypes(include=np.number).columns)[:int(remaining_cols)-1]
                        selected_cols = selected_cols.tolist() + remaining_numeric_cols
                    else:
                        remaining_numeric_cols = list(right_client.select_dtypes(include=np.number).columns)[:int(remaining_cols)+1]
                        selected_cols = selected_cols.tolist() + remaining_numeric_cols

                result = client_copy[selected_cols]
                numeric_cols = [col for col in result.columns if all(c.isdigit() or c == 'E' for c in col)]
                numeric_cols.sort()
                new_cols = ['name'] + numeric_cols
                new_df = result[new_cols]
                if new_df.shape[1] > 6:
                    new_df = new_df.drop(new_df.columns[new_df.isna().any()].values[0], axis=1)
        else:
            return client_name, client

        return client_name, new_df

    @staticmethod
    def _make_place_number(number):
        return '{0:,}'.format(round(number, 1)).replace(',', ' ') if number else number

    @staticmethod
    def make_format_msg(subject_name, articles, com_data):
        """
        Make format to message.
        :param subject_name: name of client(commodity)
        :param articles: article data about client(commodity)
        :param com_data: data about commodity pricing
        :return: formatted text
        """
        # TODO: 23 (year) автоматически обновлять ?
        com_price_first_word = {'price': 'Spot', 'm_delta': 'Δ месяц', 'y_delta': 'Δ YTD', 'cons': "Cons-s'23"}
        format_msg = f'<b>{subject_name.capitalize()}</b>'
        com_msg = ''

        if articles:
            for index, article_data in enumerate(articles):
                format_text = FormatText(title=article_data[0], date=article_data[1], link=article_data[2],
                                         text_sum=article_data[3])
                articles[index] = format_text.make_subject_text()
            all_articles = '\n\n'.join(articles)
            format_msg += f'\n\n{all_articles}'
        else:
            format_msg = True

        img_name_list = []
        if com_data:
            for com in com_data:
                # get img_name
                img_name_list.append(com["subname"].replace(' ', '_').replace('/', '_'))
                # make place between digit
                com["price"] = ArticleProcess._make_place_number(com["price"]) if not np.isnan(com['price']) else None
                com["cons"] = ArticleProcess._make_place_number(com["cons"]) if not np.isnan(com["cons"]) else None
                # create rows with commodity pricing
                subname = f'<b>{com["subname"]}</b>'
                # subname = f'<b>{com["subname"]}</b>' if len(com_data) > 1 else None
                price = f'{com_price_first_word["price"]}: <b>{com["price"]} {com["unit"]}</b>' if com[
                    "price"] else None
                m_delta = f'{com_price_first_word["m_delta"]}: <i>{com["m_delta"]} % </i>' if not np.isnan(
                    com['m_delta']) else None
                y_delta = f'{com_price_first_word["y_delta"]}: <i>{com["y_delta"]} % </i>' if not np.isnan(
                    com['y_delta']) else None
                cons = f'{com_price_first_word["cons"]}: <b>{com["cons"]} {com["unit"]}</b>' if com["cons"] else None
                # join rows
                row_list = list(filter(None, [subname, price, m_delta, y_delta, cons]))
                com_format = '\n'.join(row_list)
                com_msg += f'\n\n{com_format}'

        if subject_name == 'газ':
            com_msg = ''

        return com_msg, format_msg, img_name_list

    @staticmethod
    def make_format_industry_msg(articles):
        format_msg = ''

        if articles:
            articles_short = []
            subject = ''
            for article_data in articles:
                format_text = FormatText(subject=article_data[1], date=article_data[2],
                                         link=article_data[3], title=article_data[4], text_sum=article_data[5])
                industry_text = format_text.make_industry_text()
                if subject != format_text.subject:
                    subject = format_text.subject
                    articles_short.append(subject + industry_text)
                else:
                    articles_short.append(industry_text)
            all_articles = '\n'.join(articles_short)
            format_msg += f'{all_articles}'
        else:
            return 'Пока нет новостей на эту тему'

        format_msg = FormatText.make_industry_msg(articles[0][0], format_msg)
        return format_msg

    def process_user_alias(self, subject_id: int, subject: str = '', limit_all: int = NEWS_LIMIT + 1, offset_all: int = 0):
        """ Process user alias and return reply for it """

        com_data, reply_msg, img_name_list = None, '', []

        if subject == 'client':
            subject_name, articles = self._get_articles(subject_id, subject, limit_all, offset_all)
        elif subject == 'commodity':
            subject_name, articles = self._get_articles(subject_id, subject, limit_all, offset_all)
            com_data = self._get_commodity_pricing(subject_id)
        elif subject == 'industry':
            articles = self._get_industry_articles(subject_id)
            reply_msg = self.make_format_industry_msg(articles)
            return '', reply_msg, img_name_list
        else:
            # данный случай не вызывается
            print('user do not want articles')
            return '', False, img_name_list

        com_cotirov, reply_msg, img_name_list = self.make_format_msg(subject_name, articles, com_data)

        if subject_id and not articles and ((subject == 'client') or (not img_name_list and subject == 'commodity')):
            self._logger.warning(f'По {subject_name} не найдены новости')
            reply_msg = f'<b>{subject_name.capitalize()}</b>\n\nПока нет новостей на эту тему'

        return com_cotirov, reply_msg, img_name_list

    def get_news_by_time(self, hours: int, table: str, columns: str = '*'):
        """
        Получить таблицу с новостями по клиенту/комоде/*индустрии за последние N часов

        :param hours: За сколько последних часов собрать новости? Считается как: (t - N), где N - запрашиваемое число
        :param table: Какая таблица интересует для сбора (commodity, client)?
        :param columns: Какие колонки необходимо собрать из таблицы (пример: 'id, name, link'). Default = '*'
        return Дата Фрейм с таблицей по объекту собранной из бд
        """
        return pd.read_sql_query(f"SELECT {columns} FROM article "
                                 f"INNER JOIN relation_{table}_article ON "
                                 f"article.id = relation_{table}_article.article_id "
                                 f"INNER JOIN {table} ON relation_{table}_article.{table}_id = {table}.id "
                                 f"WHERE (date > now() - interval '{hours} hours') and {table}_score > 0 "
                                 f"ORDER BY {table}_score desc, date asc;", con=self.engine)

    def get_industry_client_com_dict(self) -> List[Dict]:
        """
        Составление словарей для новостных объектов и их альтернативных названий
        return: список со словарями клиентов, товаров и отраслей dict(id=List[other_names])
        """
        icc_dict = []
        subjects = ('industry', 'client', 'commodity')
        query = 'SELECT {subject}_id, other_names FROM {subject}_alternative'

        for subject in subjects:
            subject_df = pd.read_sql_query(query.format(subject=subject), con=self.engine)
            subject_df['other_names'] = subject_df['other_names'].str.split(';')
            subject_dict = subject_df.set_index('{}_id'.format(subject))['other_names'].to_dict()
            icc_dict.append(subject_dict)

        return icc_dict

    @staticmethod
    def get_user_article(client_article, commodity_article, industry_ids, client_ids, commodity_ids, industry_name):
        """
        Формирует два df со свежими новостями про объекты, на которые подписан пользователь.
        :param client_article: df со свежими новостями про клиентов
        :param commodity_article: df со свежими новостями про коммоды
        :param industry_ids: id отраслей, на которые подписан пользователь
        :param client_ids: id клиентов, на которых подписан пользователь
        :param commodity_ids: id коммодов, на которые подписан пользователь
        :param industry_name: dict с id отрасли в качества ключа и названия отрасли в качестве значения
        return: df с отраслевыми новостями, df с новостями по клиентам и коммодам
        """

        # получим новости по отраслям, на которые подписан пользователь
        cols = ['name', 'date', 'link', 'title', 'text_sum', 'industry_id']
        all_article = pd.concat([client_article[cols], commodity_article[cols]], ignore_index=True)
        industry_article_df = all_article[all_article['industry_id'].isin(industry_ids)].drop_duplicates(subset='link')
        industry_article_df.insert(0, 'industry', industry_article_df['industry_id'].apply(lambda x: industry_name[x]))
        industry_article_df['date'] = ''

        # получим новости по клиентам и коммодам, на которые подписан пользователь
        cols = ['title', 'date', 'link', 'text_sum', 'name']
        client_article_df = client_article.loc[client_article['client_id'].isin(client_ids)][cols]
        commodity_article_df = commodity_article.loc[commodity_article['commodity_id'].isin(commodity_ids)][cols]
        client_commodity_article_df = pd.concat([client_article_df, commodity_article_df], ignore_index=True)

        # удалим из клиентов_коммодов новости, которые есть в отраслевых новостях, а также дубли
        common_links = client_commodity_article_df['link'].isin(industry_article_df['link'])
        client_commodity_article_df = client_commodity_article_df[~common_links].drop_duplicates(subset='link')
        client_commodity_article_df[['date', 'text_sum']] = ''

        return industry_article_df, client_commodity_article_df


class ArticleProcessAdmin:

    def __init__(self):
        self.engine = create_engine(psql_engine, poolclass=NullPool)

    def get_article_id_by_link(self, link: str):
        try:
            with self.engine.connect() as conn:
                article_id = conn.execute(text(f"SELECT id FROM article WHERE link='{link}'")).fetchone()[0]
            return article_id
        except (TypeError, ProgrammingError):
            return

    def get_article_text_by_link(self, link: str):
        try:
            with self.engine.connect() as conn:
                article = conn.execute(text(f"SELECT text, text_sum FROM article WHERE link='{link}'")).fetchone()
                full_text, text_sum = article[0], article[1]
            return full_text, text_sum
        except (TypeError, ProgrammingError):
            return '', ''

    def get_article_by_link(self, link: str):
        dict_keys_article = ('Заголовок', 'Ссылка', 'Дата публикации', 'Саммари')
        dict_keys_client = ('Клиент', 'Балл по клиенту')
        dict_keys_commodity = ('Товар', 'Балл по товару')

        query_article = f"SELECT title, link, date, text_sum FROM article WHERE link='{link}'"

        query_client = (
            f"SELECT STRING_AGG(name, '; '), r_cli.client_score "
            f"FROM client "
            f"JOIN relation_client_article r_cli ON r_cli.client_id = client.id "
            f"JOIN article ON article.id = r_cli.article_id "
            f"WHERE link = '{link}' "
            f"GROUP BY r_cli.client_score")

        query_commodity = (
            f"SELECT  STRING_AGG(name, '; '), r_com.commodity_score "
            f"FROM commodity "
            f"JOIN relation_commodity_article r_com ON r_com.commodity_id = commodity.id "
            f"JOIN article ON article.id = r_com.article_id "
            f"WHERE link = '{link}' "
            f"GROUP BY r_com.commodity_score")

        try:
            with self.engine.connect() as conn:
                article_data = conn.execute(text(query_article)).fetchone()
                article_client = conn.execute(text(query_client)).fetchone()
                article_commodity = conn.execute(text(query_commodity)).fetchone()

                article_data_dict = {key: val for key, val in zip(dict_keys_article, article_data)}

                if article_client:
                    article_client_dict = {key: val for key, val in zip(dict_keys_client, article_client)}
                else:
                    article_client_dict = dict.fromkeys(dict_keys_client, '-')

                if article_commodity:
                    article_commodity_dict = {key: val for key, val in zip(dict_keys_commodity, article_commodity)}
                else:
                    article_commodity_dict = dict.fromkeys(dict_keys_commodity, '-')

            summary = article_data_dict.pop('Саммари')
            article_data_dict.update(article_client_dict)
            article_data_dict.update(article_commodity_dict)
            article_data_dict.update({'Саммари': summary})
            data = article_data_dict.copy()

            return data
        # except (TypeError, ProgrammingError):
        except Exception as e:
            return e

    def change_score_article_by_id(self, article_id: int):
        try:
            with self.engine.connect() as conn:
                query = 'update relation_{subject}_article set {subject}_score=0 where article_id={id}'
                conn.execute(text(query.format(subject='client', id=article_id)))
                conn.execute(text(query.format(subject='commodity', id=article_id)))
                conn.commit()
                return True
        except (TypeError, ProgrammingError):
            return False

    def insert_new_gpt_summary(self, new_text_summary, link):
        """ Insert new gpt summary into database """
        with self.engine.connect() as conn:
            conn.execute(text(f"UPDATE article SET text_sum=('{new_text_summary}') where link='{link}'"))
            conn.commit()


class FormatText:
    """  Форматирует текст для передачи в Телеграмм  """
    MARKER = '&#128204;'

    def __init__(self, subject: str = '', date: Union[dt.datetime, str] = '', link: str = '',
                 title: str = '', text_sum: str = ''):
        self.__subject = subject  # имя клиента/товара
        self.__title = title
        self.__date = date
        self.__link = link
        self.__text_sum = text_sum

    @property
    def subject(self):
        """ Возвращает отформатированное имя клиента/товара """
        return f'\n<b>{self.__subject.capitalize()}</b>\n'

    @property
    def title(self):
        title = self.__title
        return self.text_sum.split('.')[0] if not title else title

    @property
    def date(self):
        if self.__date:
            return f'\n<i>{self.__date.strftime("%d.%m.%Y")}</i>'
        else:
            return self.__date

    @property
    def link(self):
        url = urlparse(self.__link)
        base_url = url.netloc.split('www.')[-1]
        if base_url == 't.me':
            base_url = f"{base_url}/{url.path.split('/')[1]}"
        return f'<a href="{self.__link}">{base_url}</a>'

    @property
    def text_sum(self):
        text_sum = self.__text_sum
        return f'{text_sum}.' if text_sum[-1] != '.' else text_sum

    def make_subject_text(self):
        """ Возвращает новостной текст для клиента/товара """
        if self.__title and self.__text_sum:
            return f'{self.MARKER} <b>{self.__title}</b>\n{self.text_sum} {self.link}{self.date}'
        elif self.__title and not self.__text_sum:
            return f'{self.MARKER} {self.__title} {self.link}{self.date}'
        elif not self.__title and self.__text_sum:
            return f'{self.MARKER} {self.text_sum} {self.link}{self.date}'
        else:
            raise Exception(f'У новости нет заголовка и саммари, ссылка: {self.__link}')

    def make_industry_text(self):
        """ Возвращает новостной текст для просмотра новостей про индустрию """
        msg = f'{self.MARKER} {self.title} {self.link}{self.date}'
        return msg

    @staticmethod
    def make_industry_msg(industry, format_msg):
        """ Возвращает сообщение с новостями об индустрии """
        industry = f'<b>{industry.upper()}</b>\n'
        industry_description = '<b>Подборка новостей отрасли</b>\n'
        return '{}{}{}'.format(industry, industry_description, format_msg)

