import pandas as pd
from sqlalchemy import create_engine, text
import os
import datetime as dt
from config import psql_engine

# TODO: решить какой минимальный коэффициент, и время жизни новости
MIN_RELEVANT_VALUE = 60
TIME_LIVE_ARTICLE = 7


class ArticleError(Exception):
    pass


class ArticleProcess:
    def __init__(self):
        # TODO: psql_engine
        self.engine = create_engine(psql_engine)
        self.df_article = pd.DataFrame()  # original dataframe with data about article

    # @staticmethod
    # def get_filename(dir_path):
    #     list_of_files = [filename for filename in os.listdir(dir_path)]
    #     filename = '' if not list_of_files else list_of_files[0]
    #     return filename

    @staticmethod
    def load_client_file(client_filepath: str) -> pd.DataFrame:
        """
        Load and process client articles file.
        :param client_filepath: file path to Excel file with clients articles
        :return: dataframe of articles
        """
        new_name_client_columns = {'url': 'link', 'title': 'title', 'date': 'date', 'New Topic Confidence': 'coef',
                                   'text': 'text', 'text Summary': 'text_sum', 'Company_name': 'client'}
        df_client = pd.read_csv(client_filepath, index_col=False).rename(columns=new_name_client_columns)
        df_client = df_client[['link', 'title', 'date', 'text', 'text_sum', 'client']][df_client.coef > MIN_RELEVANT_VALUE]
        df_client['date'] = df_client['date'].apply(lambda x: dt.datetime.strptime(x, '%m/%d/%Y %H:%M:%S %p'))
        df_client['title'] = df_client['title'].apply(lambda x: None if x == '0' else x)
        df_client.client = df_client.client.str.lower()

        return df_client

    @staticmethod
    def load_commodity_file(commodity_filepath: str) -> pd.DataFrame:
        """
        Load commodity articles file.
        :param commodity_filepath: file path to Excel file with clients articles
        :return: dataframe of articles
        """

        new_name_commodity_columns = {'url': 'link', 'title': 'title', 'date': 'date',
                                      'text': 'text', 'Металл': 'commodity'}
        df_commodity = pd.read_csv(commodity_filepath, index_col=False).rename(columns=new_name_commodity_columns)
        df_commodity = df_commodity[['link', 'title', 'date', 'text', 'commodity']]
        df_commodity['date'] = df_commodity['date'].apply(lambda x: dt.datetime.strptime(x, '%m/%d/%Y %H:%M:%S %p'))
        df_commodity['title'] = df_commodity['title'].apply(lambda x: None if x == '0' else x)
        df_commodity.commodity = df_commodity.commodity.str.lower()

        return df_commodity

    def delete_old_article(self):
        with self.engine.connect() as conn:
            dt_now = dt.datetime.now()
            conn.execute(text(f"DELETE FROM article WHERE '{dt_now}' - date > '{TIME_LIVE_ARTICLE} day'"))
            conn.commit()

    def throw_the_models(self, name: str, df_subject: pd.DataFrame) -> pd.DataFrame:
        df_subject[f'{name}_score'] = None
        return df_subject

    def merge_client_commodity_article(self, df_client: pd.DataFrame, df_commodity: pd.DataFrame):
        """
        Merge df of client and commodity and drop duplicates
        And set it in self.df_article.
        :param df_client: df with client article
        :param df_commodity: df with commodity article
        """
        # find common link in client and commodity article, and take client from these article
        df_link_client = df_client[['link', 'client']][df_client['link'].isin(df_commodity['link'])]
        # make df bases on common links, which contains client and commodity name
        df_client_commodity = df_commodity.merge(df_link_client, on='link')
        # remove from df_client and df_commodity common links
        df_commodity = df_commodity[~df_commodity['link'].isin(df_link_client['link'])]
        df_client = df_client[~df_client['link'].isin(df_link_client['link'])]
        # concat all df in one, so there are no duplicates and contain all data
        df_article = pd.concat([df_client, df_commodity, df_client_commodity], ignore_index=True)
        self.df_article = df_article[['link', 'title', 'date', 'text', 'text_sum', 'client', 'commodity',
                                      'client_score', 'commodity_score']]

    def save_tables(self) -> None:
        """
        Save article, get ids for original df from db,
        And call make_save method for relation table.
        """

        # filter dubl news if they in DB and in new df
        links_value = ", ".join([f"'{link}'" for link in self.df_article["link"].values.tolist()])
        query_old_article = f'SELECT link FROM article WHERE link IN ({links_value})'
        links_of_old_article = pd.read_sql(query_old_article, con=self.engine)
        if not links_of_old_article.empty:
            self.df_article = self.df_article[~self.df_article['link'].isin(links_of_old_article.link)]

        # make article table and save it in database
        article = self.df_article[['link', 'title', 'date', 'text', 'text_sum']]
        article.to_sql('article', con=self.engine, if_exists='append', index=False)

        # add ids to df_article from article table from db
        query_ids = f"SELECT id, link FROM article WHERE link IN ({links_value})"
        ids = pd.read_sql(query_ids, con=self.engine)

        # merge ids from db with df_article
        self.df_article = self.df_article.merge(pd.DataFrame(ids), on='link')

        # make relation tables between articles and client and commodity
        self.make_save_relation_article_table('client')
        self.make_save_relation_article_table('commodity')

    def make_save_relation_article_table(self, name: str) -> None:
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