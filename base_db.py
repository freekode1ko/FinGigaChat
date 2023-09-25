from sqlalchemy import create_engine, text
import pandas as pd
from config import psql_engine

CLIENT_NAME_PATH = 'data/name/client_name.csv'
COMMODITY_NAME_PATH = 'data/name/commodity_name.csv'
CLIENT_ALTERNATIVE_NAME_PATH = 'data/name/client_with_alternative_names.xlsx'
COMMODITY_ALTERNATIVE_NAME_PATH = 'data/name/commodity_with_alternative_names.xlsx'


def make_alternative_tables(engine, subject, filepath):
    """ Make values for table with alternative names """

    df_alternative_names = pd.read_excel(filepath, index_col=False)
    df_alternative_names = df_alternative_names.applymap(lambda x: x.lower().strip() if isinstance(x, str) else x)
    df_subject = pd.read_sql(f'SELECT id, name FROM {subject}', con=engine)
    names_list = []

    for alternative_names in df_alternative_names.values.tolist():
        main_name = alternative_names[0]
        names = ';'.join([name.replace("'", "''") for name in alternative_names if pd.notna(name)])
        subject_id = df_subject['id'][df_subject['name'] == main_name].values[0]
        names_list.append(f"({subject_id}, '{names}')")

    values = ", ".join(names_list)
    query_insert = f'INSERT INTO public.{subject}_alternative ({subject}_id, other_names) VALUES {values}'

    return query_insert


def main(engine):
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
    queries = [query_client, query_commodity, query_article,
               query_relation_client, query_relation_commodity,
               query_client_alternative, query_commodity_alternative,
               query_chat, query_message, query_relation_client_msg, query_relation_commodity_msg]

    with engine.connect() as conn:
        for query in queries:
            conn.execute(text(query))
        conn.commit()

    # insert client names in client table
    df_client = pd.read_csv(CLIENT_NAME_PATH, index_col=False)
    df_client.name = df_client.name.str.lower()
    df_client.to_sql('client', con=engine, if_exists='append', index=False)

    # insert commodity names in commodity table
    df_commodity = pd.read_csv(COMMODITY_NAME_PATH, index_col=False)
    df_commodity.name = df_commodity.name.str.lower()
    df_commodity.to_sql('commodity', con=engine, if_exists='append', index=False)

    # make query to insert alternative client names in client_alternative table
    query_alternative_client_insert = make_alternative_tables(engine, 'client', CLIENT_ALTERNATIVE_NAME_PATH)

    # make query to insert alternative commodity names in commodity_alternative table
    query_alternative_commodity_insert = make_alternative_tables(engine, 'commodity', COMMODITY_ALTERNATIVE_NAME_PATH)

    with engine.connect() as conn:
        conn.execute(text(query_alternative_client_insert))
        conn.execute(text(query_alternative_commodity_insert))
        conn.commit()


def update_database(engine, query: str):
    """ Update database by query """
    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()


query_commodity_pricing = ('CREATE TABLE IF NOT EXISTS public.commodity_pricing'
                           '('
                           'id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                           'commodity_id integer NOT NULL,'
                           'subname text NOT NULL,'
                           'unit text,'
                           'price float,'
                           'm_delta float,'
                           'y_delta float,'
                           'cons float,'
                           'CONSTRAINT commodity_pricing_pkey PRIMARY KEY (id),'
                           'CONSTRAINT commodity_id FOREIGN KEY (commodity_id)'
                           '   REFERENCES public.commodity (id) MATCH SIMPLE'
                           '   ON UPDATE CASCADE'
                           '   ON DELETE CASCADE'
                           ')'
                           'TABLESPACE pg_default;')

query_commodity_energy = "INSERT INTO public.commodity (name) VALUES ('электроэнергия')"
query_delete_dupl = "DELETE FROM commodity a USING commodity b WHERE a.id < b.id AND a.name = b.name;"
query_commodity_olovo = "INSERT INTO public.commodity (name) VALUES ('олово')"
query_new_alternative_com_olovo = ("INSERT INTO public.commodity_alternative (commodity_id, other_names) "
                                   "values ((SELECT id FROM public.commodity WHERE name = 'олово'), 'олово')")
query_new_alternative_com_electro = ("INSERT INTO public.commodity_alternative (commodity_id, other_names) "
                                   "values ((SELECT id FROM public.commodity WHERE name = 'электроэнергия'), 'электроэнергия')")

gas_name = 'группа "газ"'
query_update_gas_client_name = (f"UPDATE client_alternative SET other_names=('{gas_name};горьковский автомобильный завод;группа газ') "
                                f"WHERE other_names='газ;группа «газ»;горьковский автомобильный завод';")

if __name__ == '__main__':
    main_engine = create_engine(psql_engine)
    # create base table and full it
    # main(main_engine)
    # # create commodity_pricing
    # update_database(main_engine, query_commodity_pricing)
    # # add energy in commodity
    # update_database(main_engine, query_commodity_energy)
    # # delete duplicate commodity
    # update_database(main_engine, query_delete_dupl)
    # # insert new com: olovo
    # update_database(main_engine, query_commodity_olovo)
    # # insert alternative name for new com
    # update_database(main_engine, query_new_alternative_com_electro)
    # update_database(main_engine, query_new_alternative_com_olovo)
    # update gas client name
    update_database(main_engine, query_update_gas_client_name)
