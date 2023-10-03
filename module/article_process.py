import os
import datetime as dt
import numpy as np
import re
import urllib.parse

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

from config import psql_engine
from module.model_pipe import deduplicate, model_func


TIME_LIVE_ARTICLE = 5
NOT_RELEVANT_EXPRESSION = ['читайте также', 'беспилотник', 'смотрите']


class ArticleError(Exception):
    pass


class ArticleProcess:
    def __init__(self):
        # TODO: psql_engine
        self.engine = create_engine(psql_engine)
        self.df_article = pd.DataFrame()  # original dataframe with data about article

    @staticmethod
    def get_filename(dir_path):
        list_of_files = [filename for filename in os.listdir(dir_path)]
        filename = '' if not list_of_files else list_of_files[0]
        return filename

    @staticmethod
    def load_file(filepath: str, type_of_article: str) -> pd.DataFrame:
        """
        Load and process articles file.
        :param filepath: file path to Excel file with articles
        :param type_of_article: type of article (client or commodity)
        :return: dataframe of articles
        """
        if type_of_article == 'client':
            new_name_columns = {'url': 'link', 'title': 'title', 'date': 'date', 'New Topic Confidence': 'coef',
                                'text': 'text', 'text Summary Summary': 'text_sum', 'Company_name': 'client'}
            columns = ['link', 'title', 'date', 'text', 'text_sum', 'client']
        else:
            new_name_columns = {'url': 'link', 'title': 'title', 'date': 'date', 'text': 'text', 'Металл': 'commodity'}
            columns = ['link', 'title', 'date', 'text', 'commodity']

        df_subject = pd.read_csv(filepath, index_col=False).rename(columns=new_name_columns)
        df_subject = df_subject[columns]
        df_subject['text'] = df_subject['text'].str.replace('«', '"').replace('»', '"')
        df_subject['date'] = df_subject['date'].apply(lambda x: dt.datetime.strptime(x, '%m/%d/%Y %H:%M:%S %p'))
        df_subject['title'] = df_subject['title'].apply(lambda x: None if x == '0' else x)
        df_subject[type_of_article] = df_subject[type_of_article].str.lower()

        return df_subject

    @staticmethod
    def throw_the_models(df_subject: pd.DataFrame,  name: str,) -> pd.DataFrame:
        """ Call model pipe func """
        df_subject = model_func(df_subject, name)
        return df_subject

    def drop_duplicate(self):
        """ Call func to delete similar articles """
        old_articles = pd.read_sql('SELECT text from article', con=self.engine)
        print('-- new article before deduplicate = ', len(self.df_article))
        self.df_article = deduplicate(self.df_article, old_articles)
        print('-- new article after deduplicate = ', len(self.df_article))

    def delete_old_article(self):
        with self.engine.connect() as conn:
            dt_now = dt.datetime.now()
            conn.execute(text(f"DELETE FROM article WHERE '{dt_now}' - date > '{TIME_LIVE_ARTICLE} day'"))
            conn.commit()

    def merge_client_commodity_article(self, df_client: pd.DataFrame, df_commodity: pd.DataFrame):
        """
        Merge df of client and commodity and drop duplicates
        And set it in self.df_article.
        :param df_client: df with client article
        :param df_commodity: df with commodity article
        """
        # find common link in client and commodity article, and take client from these article
        df_link_client = df_client[['link', 'client', 'client_score']][df_client['link'].isin(df_commodity['link'])]
        # make df bases on common links, which contains client and commodity name
        df_client_commodity = df_commodity.merge(df_link_client, on='link')
        # remove from df_client and df_commodity common links
        df_commodity = df_commodity[~df_commodity['link'].isin(df_link_client['link'])]
        df_client = df_client[~df_client['link'].isin(df_link_client['link'])]
        # concat all df in one, so there are no duplicates and contain all data
        df_article = pd.concat([df_client, df_commodity, df_client_commodity], ignore_index=True)
        self.df_article = df_article[['link', 'title', 'date', 'text', 'text_sum', 'client', 'commodity',
                                      'client_score', 'commodity_score', 'cleaned_data']]
        print(f'-- common article in commodity and client files is {len(df_client_commodity)}')

    def save_tables(self) -> None:
        """
        Save article, get ids for original df from db,
        And call make_save method for relation table.
        """
        # TODO: оставляет 8 дублирующих новостей
        # filter dubl news if they in DB and in new df
        links_value = ", ".join([f"'{urllib.parse.unquote(link)}'" for link in self.df_article["link"].values.tolist()])
        query_old_article = f'SELECT link FROM article WHERE link IN ({links_value})'
        links_of_old_article = pd.read_sql(query_old_article, con=self.engine)
        if not links_of_old_article.empty:
            print('-- there are old articles in these batch !!!')
            self.df_article = self.df_article[~self.df_article['link'].isin(links_of_old_article.link)]

        # make article table and save it in database
        article = self.df_article[['link', 'title', 'date', 'text', 'text_sum']]
        article.to_sql('article', con=self.engine, if_exists='append', index=False)
        print(f'-- save {len(article)} articles in database')

        # add ids to df_article from article table from db
        query_ids = f"SELECT id, link FROM article WHERE link IN ({links_value})"
        ids = pd.read_sql(query_ids, con=self.engine)

        # merge ids from db with df_article
        self.df_article = self.df_article.merge(pd.DataFrame(ids), on='link')

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
        print(f'-- relation_{name}_article is {len(df_relation_subject_article)}')

    def _find_subject_id(self, message: str, subject: str):
        """
        Find id of client or commodity by user message
        :param message: user massage
        :param subject: client or commodity
        :return: id of client(commodity) or False if user message not about client or commodity
        """

        message_text = message.lower().strip()
        df_alternative = pd.read_sql(f'SELECT {subject}_id, other_names FROM {subject}_alternative', con=self.engine)
        df_alternative['other_names'] = df_alternative['other_names'].apply(lambda x: x.split(';'))

        for subject_id, names in zip(df_alternative[f'{subject}_id'], df_alternative['other_names']):
            if message_text in names:
                return subject_id
        return False

    def _get_articles(self, subject_id: int, subject: str):
        """
        Get sorted sum article by subject id.
        :param subject_id: id of client or commodity
        :param subject: client or commodity
        :return: name of client(commodity) and sorted sum articles
        """
        with self.engine.connect() as conn:
            query_article_data = (f'SELECT relation.article_id, relation.{subject}_score, '
                                  f'article_.date, article_.link, article_.text_sum '
                                  f'FROM relation_{subject}_article AS relation '
                                  f'INNER JOIN ('
                                  f'SELECT id, date, link, text_sum '
                                  f'FROM article '
                                  f') AS article_ '
                                  f'ON article_.id = relation.article_id '
                                  f'WHERE relation.{subject}_id = {subject_id} AND relation.{subject}_score <> 0 '
                                  f'ORDER BY date DESC, relation.{subject}_score DESC '
                                  f'LIMIT 5')

            article_data = [item[2:] for item in conn.execute(text(query_article_data))]
            name = conn.execute(text(f'SELECT name FROM {subject} WHERE id={subject_id}')).fetchone()[0]

            return name, article_data

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
        marker = '&#128204;'
        # TODO: 23 (year) автоматически обновлять ?
        com_price_first_word = {'price': 'Spot', 'm_delta': 'Δ месяц', 'y_delta': 'Δ YTD', 'cons': "Cons-s'23"}
        format_msg = f'<b>{subject_name.capitalize()}</b>'

        if articles:
            for index, article_data in enumerate(articles):
                date, link, text_sum = article_data[0], article_data[1], article_data[2]
                date = date.strftime('%d.%m.%Y')
                link_phrase = f'<a href="{link}">Источник</a>'
                text_sum = f'{text_sum}.' if text_sum[-1] != '.' else text_sum
                articles[index] = f'{marker} {text_sum} {link_phrase}\n<i>{date}</i>'
            all_articles = '\n\n'.join(articles)
            format_msg += f'\n\n{all_articles}'

        img_name_list = []
        if com_data:
            for com in com_data:
                # get img_name
                img_name_list.append(com["subname"].replace(' ', '_').replace('/', '_'))
                # make place between digit
                com["price"] = ArticleProcess._make_place_number(com["price"]) if not np.isnan(com['price']) else None
                com["cons"] = ArticleProcess._make_place_number(com["cons"]) if not np.isnan(com["cons"]) else None
                # create rows with commodity pricing
                subname = f'<b>{com["subname"]}</b>' if len(com_data) > 1 else None
                price = f'{com_price_first_word["price"]}: <b>{com["price"]} {com["unit"]}</b>' if com["price"] else None
                m_delta = f'{com_price_first_word["m_delta"]}: <i>{com["m_delta"]} % </i>' if not np.isnan(com['m_delta']) else None
                y_delta = f'{com_price_first_word["y_delta"]}: <i>{com["y_delta"]} % </i>' if not np.isnan(com['y_delta']) else None
                cons = f'{com_price_first_word["cons"]}: <b>{com["cons"]} {com["unit"]}</b>' if com["cons"] else None
                # join rows
                row_list = list(filter(None, [subname, price, m_delta, y_delta, cons]))
                com_format = '\n'.join(row_list)
                format_msg += f'\n\n{com_format}'

        return format_msg, img_name_list

    def process_user_alias(self, message: str):
        """ Process user alias and return reply for it """
        com_data, reply_msg, img_name_list = None, '', []
        client_id, commodity_id = '', ''
        client_id = self._find_subject_id(message, 'client')
        if client_id:
            subject_name, articles = self._get_articles(client_id, 'client')
        else:
            commodity_id = self._find_subject_id(message, 'commodity')
            if commodity_id:
                subject_name, articles = self._get_articles(commodity_id, 'commodity')
                com_data = self._get_commodity_pricing(commodity_id)
            else:
                print('user do not want articles')
                return False, img_name_list

        reply_msg, img_name_list = self.make_format_msg(subject_name, articles, com_data)

        if client_id and not articles:
            return 'Пока нет новостей на эту тему', img_name_list
        elif commodity_id and not articles and not img_name_list:
            return 'Пока нет новостей на эту тему', img_name_list

        return reply_msg, img_name_list


class ArticleProcessAdmin:

    def __init__(self):
        self.engine = create_engine(psql_engine)

    def get_article_text_by_link(self, link: str):
        try:
            with self.engine.connect() as conn:
                article = conn.execute(text(f"SELECT * FROM article WHERE link='{link}'")).fetchone()
                full_text, text_sum = article[4], article[5]
        except (TypeError, ProgrammingError):
            return '', ''
        else:
            return full_text, text_sum

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

    def delete_article_by_link(self, link: str):
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"DELETE FROM article WHERE link='{link}'"))
                conn.commit()
        except (TypeError, ProgrammingError):
            return False
        else:
            return True

    def insert_new_gpt_summary(self, new_text_summary, link):
        """ Insert new gpt summary into database """
        with self.engine.connect() as conn:
            conn.execute(text(f"UPDATE article SET text_sum=('{new_text_summary}') where link='{link}'"))
            conn.commit()

    @staticmethod
    def find_not_relevant_news(article: str):
        for expression in NOT_RELEVANT_EXPRESSION:
            article = article.lower()
            regular = f'{expression}'
            if re.search(regular, article):
                return False
            else:
                return True

    def get_bad_article(self):
        """ Get article data if it contains bad word """
        # TODO: как отправлять большее количество новостей

        df = pd.read_sql("SELECT link, text FROM article ORDER BY date DESC", con=self.engine)
        df['relevant'] = df['text'].apply(lambda x: ArticleProcessAdmin.find_not_relevant_news(x))
        df = df[~df['relevant']]
        bad_links = df['link'].values.tolist()
        msgs = []
        for link in bad_links:
            msgs.append(self.get_article_by_link(link))
        return msgs[:5]





