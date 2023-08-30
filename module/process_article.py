import pandas as pd
from sqlalchemy import create_engine, text
import os

# TODO: решить какой минимальный коэффициент
MIN_RELEVANT_VALUE = 60


class ArticleError(Exception):
    pass


class ArticleProcess:
    def __init__(self):
        # TODO: psql_engine
        psql_engine = 'postgresql+psycopg2://postgres:lolakibaba1997@localhost:5432/tg_parse'
        self.engine = create_engine(psql_engine)

        self.df_article = pd.DataFrame()  # original dataframe with data about article

    @staticmethod
    def load_article_files(client_filepath: str, commodity_filepath: str) -> pd.DataFrame:
        """
        Load client and commodity articles files, join it and delete duplicates.
        :param client_filepath: file path to Excel file with clients articles
        :param commodity_filepath: file path to Excel file with clients articles
        :return: dataframe of articles
        """
        # load client file
        new_name_client_columns = {'url': 'link', 'ЗАГОЛОВОК НОВОСТИ': 'title', 'date': 'date',
                                   'text': 'text', 'text_sum': 'text_sum', 'client': 'client',
                                   'coef': 'coef'}
        df_client = pd.read_excel(client_filepath, index_col=False).rename(columns=new_name_client_columns)
        df_client = df_client[['link', 'title', 'date', 'text', 'text_sum', 'client']][
            df_client.coef > MIN_RELEVANT_VALUE]

        # load commodity file
        new_name_commodity_columns = {'url': 'link', 'ЗАГОЛОВОК НОВОСТИ': 'title', 'date': 'date',
                                      'text': 'text', 'client': 'client', 'commodity': 'commodity'}
        df_commodity = pd.read_excel(commodity_filepath, index_col=False).rename(columns=new_name_commodity_columns)
        df_commodity = df_commodity[['link', 'title', 'date', 'text', 'client', 'commodity']]

        # join tables [['link', 'title', 'date', 'text', 'text_sum', 'client', 'commodity']]
        df_article = pd.concat([df_client, df_commodity], ignore_index=True)
        # drop duplicates and save last
        df_article.drop_duplicates(subset='link', keep='last', ignore_index=True, inplace=True)

        return df_article

    def set_df_article(self, client_filepath: str, commodity_filepath: str):
        self.df_article = ArticleProcess.load_article_files(client_filepath, commodity_filepath)

    def process_articles(self):
        # sorted
        # TODO: pipe for models ? + client and commodity score
        self.df_article['client_score'] = None
        self.df_article['commodity_score'] = None

    def save_tables(self) -> None:
        """
        Save article, get ids for original df from db,
        And call make_save method for relation table.
        """

        # make article table and save it in database
        # TODO: title can have "0" value
        article = self.df_article[['link', 'title', 'date', 'text', 'text_sum']]
        article.to_sql('article', con=self.engine, if_exists='append', index=False)

        # add ids to df_article from article table from db
        links_value = ", ".join([f"'{link}'" for link in self.df_article["link"].values.tolist()])
        query_ids = f"SELECT id, link FROM article WHERE link IN ({links_value})"
        ids = pd.read_sql(query_ids, con=self.engine)

        # merge ids from db with df_article
        self.df_article = self.df_article.merge(pd.DataFrame(ids), on='link')

        # make relation tables between articles and client and commodity
        self.make_save_relation_article_table('client')
        self.make_save_relation_article_table('commodity')

    def make_save_relation_article_table(self, name: str) -> None:
        """"
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