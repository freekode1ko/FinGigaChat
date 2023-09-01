from sqlalchemy import create_engine, text
import pandas as pd
from config import psql_engine

# TODO: изменить название тэйбл спейс и схемы


def main():

    # query to make client table
    query_client = ('CREATE TABLE IF NOT EXISTS public.client '
                    '('
                    'id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                    'name text NOT NULL,'
                    'CONSTRAINT client_pkey PRIMARY KEY (id)'
                    ')'
                    'TABLESPACE pg_default;')

    # query to make commodity table
    query_commodity = ('CREATE TABLE IF NOT EXISTS public.commodity '
                       '('
                       'id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                       'name text NOT NULL,'
                       'CONSTRAINT commodity_pkey PRIMARY KEY (id)'
                       ')'
                       'TABLESPACE pg_default;')

    # query to make article table
    query_article = ('CREATE TABLE IF NOT EXISTS public.article'
                     '('
                     'id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                     'link text NOT NULL,'
                     'title text NOT NULL,'
                     'date timestamp without time zone NOT NULL,'
                     'text text NOT NULL,'
                     'text_sum text,'
                     'CONSTRAINT article_pkey PRIMARY KEY (id)'
                     ')'
                     'TABLESPACE pg_default;')

    # create relation_client_article
    query_relation_client = ('CREATE TABLE IF NOT EXISTS public.relation_client_article'
                             '('
                             'client_id integer NOT NULL,'
                             'article_id integer NOT NULL,'
                             'client_score integer,'
                             'CONSTRAINT relation_client_article_pkey PRIMARY KEY (client_id, article_id), '
                             'CONSTRAINT client_id FOREIGN KEY (client_id)'
                             '  REFERENCES public.client (id) MATCH SIMPLE'
                             '  ON UPDATE CASCADE'
                             '  ON DELETE CASCADE,'
                             'CONSTRAINT article_id FOREIGN KEY (article_id)'
                             '  REFERENCES public.article (id) MATCH SIMPLE'
                             '  ON UPDATE CASCADE'
                             '  ON DELETE CASCADE'
                             ')'
                             'TABLESPACE pg_default;')

    # create relation_commodity_article
    query_relation_commodity = ('CREATE TABLE IF NOT EXISTS relation_commodity_article '
                                '('
                                'commodity_id integer NOT NULL,'
                                'article_id integer NOT NULL,'
                                'commodity_score integer, '
                                'CONSTRAINT relation_commodity_article_pkey PRIMARY KEY (commodity_id, article_id),'
                                'CONSTRAINT commodity_id FOREIGN KEY (commodity_id)'
                                '   REFERENCES public.commodity (id) MATCH SIMPLE'
                                '   ON UPDATE CASCADE'
                                '   ON DELETE CASCADE, '
                                'CONSTRAINT article_id FOREIGN KEY (article_id)'
                                '   REFERENCES public.article (id) MATCH SIMPLE'
                                '   ON UPDATE CASCADE'
                                '   ON DELETE CASCADE'
                                ')'
                                'TABLESPACE pg_default;')

    # create tables
    engine = create_engine(psql_engine)
    with engine.connect() as conn:
        conn.execute(text(query_client))
        conn.execute(text(query_commodity))
        conn.execute(text(query_article))
        conn.execute(text(query_relation_client))
        conn.execute(text(query_relation_commodity))
        conn.commit()

    # insert client names in client table
    df_client = pd.read_csv('data/client_name.csv', index_col=False)
    df_client.name = df_client.name.str.lower()
    df_client.to_sql('client', con=engine, if_exists='append', index=False)

    # insert commodity names in commodity table
    df_commodity = pd.read_csv('data/commodity_name.csv', index_col=False)
    df_commodity.name = df_commodity.name.str.lower()
    df_commodity.to_sql('commodity', con=engine, if_exists='append', index=False)


if __name__ == '__main__':
    main()
