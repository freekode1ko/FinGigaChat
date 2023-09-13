from sqlalchemy import create_engine, text
import pandas as pd
from config import psql_engine

# TODO: изменить название тэйбл спейс и схемы, относительные пути?
CLIENT_NAME_PATH = 'data/name/client_name.csv'
COMMODITY_NAME_PATH = 'data/name/commodity_name.csv'
CLIENT_ALTERNATIVE_NAME_PATH = 'data/name/client_with_alternative_names.xlsx'
COMMODITY_ALTERNATIVE_NAME_PATH = 'data/name/commodity_with_alternative_names.xlsx'


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
                     'title text,'
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

    # create client alternative names
    query_client_alternative = ('CREATE TABLE IF NOT EXISTS public.client_alternative'
                                '('
                                'id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                                'client_id integer NOT NULL,'
                                'other_names text,'
                                'CONSTRAINT client_alternative_pkey PRIMARY KEY (id),'
                                'CONSTRAINT client_id FOREIGN KEY (client_id)'
                                '   REFERENCES public.client (id) MATCH SIMPLE'
                                '   ON UPDATE CASCADE'
                                '   ON DELETE CASCADE'
                                ')'
                                'TABLESPACE pg_default;')

    # create commodity alternative names
    query_commodity_alternative = ('CREATE TABLE IF NOT EXISTS public.commodity_alternative'
                                   '('
                                   'id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                                   'commodity_id integer NOT NULL,'
                                   'other_names text,'
                                   'CONSTRAINT commodity_alternative_pkey PRIMARY KEY (id),'
                                   'CONSTRAINT commodity_id FOREIGN KEY (commodity_id)'
                                   '   REFERENCES public.commodity (id) MATCH SIMPLE'
                                   '   ON UPDATE CASCADE'
                                   '   ON DELETE CASCADE'
                                   ')'
                                   'TABLESPACE pg_default;')

    # create chat
    query_chat = ('CREATE TABLE IF NOT EXISTS public.chat'
                  '('
                  'id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                  'name text NOT NULL,'
                  'type text NOT NULL,'
                  'CONSTRAINT chat_pkey PRIMARY KEY (id)'
                  ')'
                  'TABLESPACE pg_default;')

    # create message
    query_message = ('CREATE TABLE IF NOT EXISTS public.message'
                     '('
                     'id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                     'chat_id integer NOT NULL, '
                     'link text, '
                     'date timestamp without time zone NOT NULL,'
                     'text text NOT NULL, '
                     'text_sum text, '
                     'CONSTRAINT message_pkey PRIMARY KEY (id),'
                     'CONSTRAINT chat_id FOREIGN KEY (chat_id)'
                     '  REFERENCES public.client (id) MATCH SIMPLE'
                     '  ON UPDATE CASCADE'
                     '  ON DELETE CASCADE'
                     ')'
                     'TABLESPACE pg_default;')

    # create relation_client_message
    query_relation_client_msg = ('CREATE TABLE IF NOT EXISTS public.relation_client_message'
                                 '('
                                 'client_id integer NOT NULL,'
                                 'message_id integer NOT NULL,'
                                 'client_score integer,'
                                 'CONSTRAINT relation_client_message_pkey PRIMARY KEY (client_id, message_id), '
                                 'CONSTRAINT client_id FOREIGN KEY (client_id)'
                                 '  REFERENCES public.client (id) MATCH SIMPLE'
                                 '  ON UPDATE CASCADE'
                                 '  ON DELETE CASCADE,'
                                 'CONSTRAINT message_id FOREIGN KEY (message_id)'
                                 '  REFERENCES public.message (id) MATCH SIMPLE'
                                 '  ON UPDATE CASCADE'
                                 '  ON DELETE CASCADE'
                                 ')'
                                 'TABLESPACE pg_default;')

    # create relation_commodity_message
    query_relation_commodity_msg = ('CREATE TABLE IF NOT EXISTS public.relation_commodity_message'
                                    '('
                                    'commodity_id integer NOT NULL,'
                                    'message_id integer NOT NULL,'
                                    'commodity_score integer, '
                                    'CONSTRAINT relation_commodity_message_pkey PRIMARY KEY (commodity_id, message_id),'
                                    'CONSTRAINT commodity_id FOREIGN KEY (commodity_id)'
                                    '   REFERENCES public.commodity (id) MATCH SIMPLE'
                                    '   ON UPDATE CASCADE'
                                    '   ON DELETE CASCADE, '
                                    'CONSTRAINT message_id FOREIGN KEY (message_id)'
                                    '   REFERENCES public.message (id) MATCH SIMPLE'
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
        conn.execute(text(query_client_alternative))
        conn.execute(text(query_commodity_alternative))
        conn.execute(text(query_chat))
        conn.execute(text(query_message))
        conn.execute(text(query_relation_client_msg))
        conn.execute(text(query_relation_commodity_msg))
        conn.commit()

    # insert client names in client table
    df_client = pd.read_csv(CLIENT_NAME_PATH, index_col=False)
    df_client.name = df_client.name.str.lower()
    df_client.to_sql('client', con=engine, if_exists='append', index=False)

    # insert commodity names in commodity table
    df_commodity = pd.read_csv(COMMODITY_NAME_PATH, index_col=False)
    df_commodity.name = df_commodity.name.str.lower()
    df_commodity.to_sql('commodity', con=engine, if_exists='append', index=False)

    # insert alternative client names in client_alternative table
    df_alternative_client_names = pd.read_excel(CLIENT_ALTERNATIVE_NAME_PATH, index_col=False)
    df_clients = pd.read_sql('SELECT id, name FROM client', con=engine)
    client_names_list = []

    for client_names in df_alternative_client_names.values.tolist():
        main_name = client_names[0].lower().strip()
        names = ';'.join([name.strip().replace("'", "''") for name in client_names if pd.notna(name)])
        client_id = df_clients['id'][df_clients['name'] == main_name].values[0]
        client_names_list.append(f"({client_id}, '{names}')")

    client_values = ", ".join(client_names_list)
    query_client_insert = f'INSERT INTO public.client_alternative (client_id, other_names) VALUES {client_values}'

    # insert alternative commodity names in commodity_alternative table
    df_alternative_commodity_names = pd.read_excel(COMMODITY_ALTERNATIVE_NAME_PATH, index_col=False)
    df_commodity = pd.read_sql('SELECT id, name FROM commodity', con=engine)
    commodity_names_list = []

    for commodity_names in df_alternative_commodity_names.values.tolist():
        main_name = commodity_names[0].lower().strip()
        names = ';'.join([name.strip().replace("'", "''") for name in commodity_names if pd.notna(name)])
        commodity_id = df_commodity['id'][df_commodity['name'] == main_name].values[0]
        commodity_names_list.append(f"({commodity_id}, '{names}')")

    commodity_values = ", ".join(commodity_names_list)
    query_commodity_insert = f'INSERT INTO public.commodity_alternative (commodity_id, other_names) VALUES {commodity_values}'

    with engine.connect() as conn:
        conn.execute(text(query_client_insert))
        conn.execute(text(query_commodity_insert))
        conn.commit()


if __name__ == '__main__':
    main()
