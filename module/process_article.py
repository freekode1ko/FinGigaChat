import pandas as pd
from sqlalchemy import create_engine, text

# TODO: решить какой минимальный коэффициент
MIN_RELEVANT_VALUE = 60


class ArticleError(Exception):
    pass


class ArticleProcess:
    def __init__(self):
        # TODO: psql_engine
        psql_engine = 'postgresql+psycopg2://postgres:lolakibaba1997@localhost:5432/tg_parse'
        self.engine = create_engine(psql_engine)

        self.df_article = pd.DataFrame()

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
        df_client = df_client[['link', 'title', 'date', 'text', 'text_sum', 'client']][df_client.coef > MIN_RELEVANT_VALUE]

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
        return self.df_article

    def save_article(self):

        article = self.df_article[['link', 'title', 'date', 'text', 'text_sum']]
        article.to_sql('article', con=self.engine, if_exists='append', index=False)
        links_value = ", ".join([f"'{link}'" for link in self.df_article["link"].values.tolist()])
        ids = pd.read_sql(f"select id from article where link IN ({links_value})", con=self.engine)
        self.df_article.insert(0, 'id', ids)


        client = pd.read_sql('select * from client', con=self.engine).rename(columns={'id': 'client_id',
                                                                                      'name': 'client'})


        # make relation df between client id and article id
        df_article_client = self.df_article.dropna(subset='client')[['id', 'client', 'client_score']]
        df_article_client.rename(columns={'id': 'article_id'}, inplace=True)
        df_relation_client_article = df_article_client.merge(client, on='client')[['client_id', 'article_id',
                                                                                      'client_score']]
        df_relation_client_article.to_sql('relation_client_article', con=self.engine, if_exists='append', index=False)
        # print(df_relation_client_article)
        # print(pd.read_sql('select * from article', con=self.engine))

