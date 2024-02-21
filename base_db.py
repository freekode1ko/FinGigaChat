import datetime

import pandas as pd
from sqlalchemy import create_engine, text

import config
from config import psql_engine, CLIENT_NAME_PATH, COMMODITY_NAME_PATH, \
    CLIENT_ALTERNATIVE_NAME_PATH, COMMODITY_ALTERNATIVE_NAME_PATH, CLIENT_ALTERNATIVE_NAME_PATH_FOR_UPDATE, \
    TELEGRAM_CHANNELS_DATA_PATH, QUOTES_SOURCES_PATH

# CLIENT_NAME_PATH = 'data/name/client_name.csv'
# COMMODITY_NAME_PATH = 'data/name/commodity_name.csv'
# CLIENT_ALTERNATIVE_NAME_PATH = 'data/name/client_with_alternative_names.xlsx'
# COMMODITY_ALTERNATIVE_NAME_PATH = 'data/name/commodity_with_alternative_names.xlsx'
# CLIENT_ALTERNATIVE_NAME_PATH_FOR_UPDATE = 'data/name/client_alternative.csv'


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
                    'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                    '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                    'name text NOT NULL,'
                    'CONSTRAINT client_pkey PRIMARY KEY (id)'
                    ')'
                    'TABLESPACE pg_default;')

    # query to make commodity table
    query_commodity = ('CREATE TABLE IF NOT EXISTS public.commodity '
                       '('
                       'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                       '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                       'name text NOT NULL,'
                       'CONSTRAINT commodity_pkey PRIMARY KEY (id)'
                       ')'
                       'TABLESPACE pg_default;')

    # query to make article table
    query_article = ('CREATE TABLE IF NOT EXISTS public.article'
                     '('
                     'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                     '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
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
                                'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                                '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
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
                                   'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                                   '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
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
                  'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                  '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                  'name text NOT NULL,'
                  'type text NOT NULL,'
                  'CONSTRAINT chat_pkey PRIMARY KEY (id)'
                  ')'
                  'TABLESPACE pg_default;')

    # create message
    query_message = ('CREATE TABLE IF NOT EXISTS public.message'
                     '('
                     'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                     '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
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

    query_whitelist = ('CREATE TABLE IF NOT EXISTS public.whitelist ('
                       'user_id integer NOT NULL, '
                       'username text NOT NULL, '
                       'email text, '
                       'user_type text NOT NULL, '
                       'user_status text NOT NULL, '
                       'CONSTRAINT user_id_pkey PRIMARY KEY (user_id)) '
                       'TABLESPACE pg_default;')

    query_date_of_last_build = ('CREATE TABLE IF NOT EXISTS public.date_of_last_build ('
                                'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                                '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
                                'date_time text NOT NULL,'
                                'CONSTRAINT date_time_pkey PRIMARY KEY (id))'
                                'TABLESPACE pg_default;')

    # create tables
    queries = [query_client, query_commodity, query_article,
               query_relation_client, query_relation_commodity,
               query_client_alternative, query_commodity_alternative,
               query_chat, query_message, query_relation_client_msg,
               query_relation_commodity_msg, query_whitelist, query_date_of_last_build]

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
                           'id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
                           '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),'
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

query_article_name_impact = ("CREATE TABLE IF NOT EXISTS public.article_name_impact "
                             "("
                             "id SERIAL PRIMARY KEY, "
                             "article_id INTEGER REFERENCES article(id) ON UPDATE CASCADE ON DELETE CASCADE, "
                             "commodity_impact JSON, "
                             "client_impact JSON, "
                             "cleaned_data TEXT)"
                             "TABLESPACE pg_default;")


query_tg_channels = (
    """
    CREATE TABLE IF NOT EXISTS public.telegram_channel
    (
        id serial PRIMARY KEY,
        name character varying(128) COLLATE pg_catalog."default" NOT NULL,
        link character varying(255) COLLATE pg_catalog."default" NOT NULL,
        industry_id integer NOT NULL
        CONSTRAINT industry_id FOREIGN KEY (industry_id)
            REFERENCES public.industry (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE,
    )
    TABLESPACE pg_default;
    COMMENT ON TABLE public.telegram_channel
        IS 'Справочник telegram каналов, из которых вынимаются новости';
    """
)
query_tg_article_relations = (
    """
    CREATE TABLE IF NOT EXISTS public.relation_telegram_article
    (
        telegram_id integer NOT NULL,
        article_id integer NOT NULL,
        telegram_score integer,
        CONSTRAINT relation_telegram_article_pkey PRIMARY KEY (telegram_id, article_id),
        CONSTRAINT article_id FOREIGN KEY (article_id)
            REFERENCES public.article (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE,
        CONSTRAINT telegram_id FOREIGN KEY (telegram_id)
            REFERENCES public.telegram_channel (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
    )
    TABLESPACE pg_default;
    COMMENT ON TABLE public.relation_telegram_article
        IS 'Связь новостей с telegram каналами';
    """
)
query_tg_subscriptions = (
    """
    CREATE TABLE IF NOT EXISTS public.user_telegram_subscription
    (
        user_id bigint NOT NULL,
        telegram_id integer NOT NULL,
        CONSTRAINT user_telegram_subscription_pkey PRIMARY KEY (user_id, telegram_id),
        CONSTRAINT telegram_id FOREIGN KEY (telegram_id)
            REFERENCES public.telegram_channel (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE,
        CONSTRAINT user_id FOREIGN KEY (user_id)
            REFERENCES public.whitelist (user_id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
    )
    TABLESPACE pg_default;
    COMMENT ON TABLE public.user_telegram_subscription
        IS 'Справочник подписок пользователя на новостые telegram каналы';
    """
)           

query_quote_group = (
    """
    CREATE TABLE IF NOT EXISTS public.quote_group
    (
        id SERIAL PRIMARY KEY,
        name character varying(64) COLLATE pg_catalog."default" NOT NULL
    )
    TABLESPACE pg_default;
    COMMENT ON TABLE public.quote_group
        IS 'Справочник выделенных среди котировок подгрупп';
    """
)
query_quote_source = (
    """
    DROP TABLE IF EXISTS public.quote_source CASCADE;
    CREATE TABLE IF NOT EXISTS public.quote_source
    (
        id SERIAL PRIMARY KEY,
        alias character varying(64) COLLATE pg_catalog."default" NOT NULL,
        block character varying(255) COLLATE pg_catalog."default" NOT NULL,
        response_format text COLLATE pg_catalog."default",
        source text COLLATE pg_catalog."default" NOT NULL,
        last_update_datetime timestamp without time zone,
        quote_group_id integer NOT NULL,
        CONSTRAINT quote_group_id FOREIGN KEY (quote_group_id)
            REFERENCES public.quote_group (id) MATCH SIMPLE
            ON UPDATE CASCADE
            ON DELETE CASCADE
    )
    TABLESPACE pg_default;
    COMMENT ON TABLE public.quote_source
        IS 'Справочник источников котировок';
    """
)

query_research_source_table = (
    """
    DROP TABLE IF EXISTS public.research_source CASCADE;
    CREATE TABLE IF NOT EXISTS public.research_source
    (
        id SERIAL PRIMARY KEY,
        name character varying(64) COLLATE pg_catalog."default" NOT NULL,
        description character varying(255) COLLATE pg_catalog."default" NOT NULL,
        response_format text COLLATE pg_catalog."default",
        source text COLLATE pg_catalog."default" NOT NULL,
        last_update_datetime timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
        previous_update_datetime timestamp without time zone DEFAULT CURRENT_TIMESTAMP
    )
    TABLESPACE pg_default;
    COMMENT ON TABLE public.quote_source
        IS 'Справочник источников CIB Research';
    """
)

query_commodity_energy = "INSERT INTO public.commodity (name) VALUES ('электроэнергия')"
query_delete_dupl = "DELETE FROM commodity a USING commodity b WHERE a.id < b.id AND a.name = b.name;"
query_commodity_olovo = "INSERT INTO public.commodity (name) VALUES ('олово')"
query_new_alternative_com_olovo = ("INSERT INTO public.commodity_alternative (commodity_id, other_names) "
                                   "values ((SELECT id FROM public.commodity WHERE name = 'олово'), 'олово')")
query_new_alternative_com_electro = ("INSERT INTO public.commodity_alternative (commodity_id, other_names) "
                                     "values ((SELECT id FROM public.commodity WHERE name = 'электроэнергия'), "
                                     "'электроэнергия')")


def update_client_alternative(engine):
    df_db = pd.read_csv(CLIENT_ALTERNATIVE_NAME_PATH_FOR_UPDATE, index_col=False, sep='#')
    with engine.connect() as conn:
        for i, row in df_db.iterrows():
            other_names = row['other_names']
            client_id = row['client_id']
            sql_text = f"update client_alternative set other_names='{other_names}' where client_id={client_id}"
            conn.execute(text(sql_text))
            conn.commit()
    print('Client_alternative table is update')


def update_tg_channels(engine):
    df_db = pd.read_excel(TELEGRAM_CHANNELS_DATA_PATH)[['name', 'link', 'industry_id']]
    df_db.to_sql('telegram_channel', con=engine, if_exists='append', index=False)
    print('Telegram channel table was updated')


def update_quote_group_table(engine) -> None:
    from utils import quotes
    groups = quotes.get_groups()

    quotes_groups_set = {g.get_group_name() for g in groups}
    quotes_groups_set = quotes_groups_set - set(pd.read_sql_table('quote_group', con=engine, columns=['name'])['name'].tolist())
    quotes_groups_df = pd.DataFrame(quotes_groups_set, columns=['name'])

    if not quotes_groups_df.empty:
        quotes_groups_df.to_sql('quote_group', con=engine, if_exists='append', index=False)


def update_quote_source_table(engine):
    from utils import quotes
    groups = quotes.get_groups()

    path = QUOTES_SOURCES_PATH
    columns_new_names = {
        'Алиас': 'alias',
        'Блок': 'block',
        'Формат ответа ': 'response_format',
        'Источник': 'source',
    }

    quotes_groups_df = pd.read_sql_table('quote_group', con=engine, columns=['id', 'name'])

    # считываем первый листок из файла,
    # отбрасываем строки, где есть пустые ячейки,
    # переименовываем колонки,
    # отбрасываем дубли
    sources_df = pd.read_excel(path)[['Алиас', 'Блок', 'Формат ответа ', 'Источник']]\
        .dropna()\
        .rename(columns=columns_new_names)\
        .drop_duplicates()

    sources_df['id'] = 0
    sources_df['last_update_datetime'] = datetime.datetime.now()
    sources_df['alias'] = sources_df['alias'].str.split('/', n=1).str[0]
    sources_df['source'] = sources_df['source'].str.rstrip('/')
    sources_df['group_name'] = ''
    sources_df = sources_df[['alias', 'id', 'block', 'source', 'response_format', 'last_update_datetime', 'group_name']]

    for i, row in sources_df.iterrows():
        for group in groups:
            if group.filter(row):
                sources_df.loc[i, 'group_name'] = group.get_group_name()
                break

    sources_df = (
        sources_df.merge(quotes_groups_df,  left_on='group_name', right_on='name', suffixes=['', '_y'])
                  .rename(columns={'id_y': 'quote_group_id'})[
            ['alias', 'block', 'response_format', 'source', 'quote_group_id', 'last_update_datetime']
        ]
    )

    sources_df.to_sql('quote_source', con=engine, if_exists='append', index=False)


def update_research_source_table(engine):
    # выгрузить данные из xlsx
    # выгрузить данные из БД
    # объединить (
    #   обновить информацию о смежных источниках
    #   источники, которые есть в БД, но нет в xlsx - удалить
    #   источники, которых нет в БД, добавить туда
    # )
    # IF THERE WILL BE SUBSCRIPTIONS ON RESEARCH SOURCES, WE HAVE TO UPDATE TABLE WITH SUBS
    path = config.RESEARCH_SOURCES_PATH
    db_cols = ['id', 'name', 'description', 'response_format', 'source', 'last_update_datetime', 'previous_update_datetime']
    sources_from_db_df = pd.read_sql_table('research_source', con=engine, columns=db_cols)

    excel_cols = ['name', 'description', 'response_format', 'source']
    # считаем здесь каждый источник уникальным по паре ключей (name, source)
    sources_df = (
        pd.read_excel(path)[excel_cols]
        .dropna(subset=['source', 'name'])
        .drop_duplicates(subset=['name', 'source'])
    )

    query = text(
        'UPDATE research_source '
        'SET name=:name, description=:description, response_format=:response_format, source=:source '
        'WHERE id=:row_id'
    )
    query_update_sources_list = []
    delete_sources_ids = []
    for _, row in sources_from_db_df.iterrows():
        # print('row')
        # print(row)
        # print('same_row in sources_df')
        # print(sources_df[(sources_df['name'] == row['name']) | (sources_df['source'] == row['source'])])
        if not (same_row := sources_df[(sources_df['name'] == row['name']) | (sources_df['source'] == row['source'])]).empty:
            # add update query, if there are new info about source
            # print(f'{all(same_row.isin(row).all().tolist())=:}')
            if all(same_row.isin(row).all().tolist()):
                continue

            # delete updated value from new values
            sources_df.drop(same_row.index.tolist(), inplace=True)
            row_id = row['id']
            same_row = same_row.to_dict(orient='records')[0]
            query_update_sources_list.append(query.bindparams(row_id=row_id, **same_row))
        else:
            delete_sources_ids.append(row['id'])

    if query_update_sources_list:
        with engine.connect() as conn:
            for q in query_update_sources_list:
                conn.execute(q)

            conn.commit()

    if delete_sources_ids:
        with engine.connect() as conn:
            query = text(
                'DELETE FROM research_source WHERE id  = ANY(:delete_sources_ids);'
            )
            conn.execute(query.bindparams(delete_sources_ids=delete_sources_ids))
            conn.commit()

    if not sources_df.empty:
        sources_df.to_sql('research_source', con=engine, if_exists='append', index=False)


def alter_to_quote_source_column(engine):
    query_alter = (
        'ALTER TABLE IF EXISTS quote_source '
        'ADD COLUMN IF NOT EXISTS previous_update_datetime timestamp with time zone;'
    )
    query_update = (
        'UPDATE quote_source SET previous_update_datetime=last_update_datetime;'
    )

    with engine.connect() as conn:
        conn.execute(text(query_alter))
        conn.execute(text(query_update))
        conn.commit()


def drop_tables(engine):
    tables = ['article', 'chat', 'client', 'client_alternative', 'commodity', 'commodity_alternative',
              'commodity_pricing', 'message', 'relation_client_message', 'relation_client_article',
              'relation_commodity_article', 'relation_commodity_message', 'article_name_impact']

    with engine.connect() as conn:
        for table in tables:
            conn.execute(text(f'DROP TABLE IF EXISTS {table} CASCADE'))
            conn.commit()
            print(f'Table {table} is down')


#  TODO: пока при вводе имен клиентов должны быть пробелы в начале и в конце
if __name__ == '__main__':
    main_engine = create_engine(psql_engine)

    # !!! DROP TABLE !!!
    # # # # drop_tables(main_engine)

    # # create base table and full it
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
    # # make article_name_count
    # update_database(main_engine, query_article_name_impact)
    # # update client_alternative
    # update_client_alternative(main_engine)

    # # add table telegram_channel
    # update_database(main_engine, query_tg_channels)
    # # add table relation_telegram_article
    # update_database(main_engine, query_tg_article_relations)
    # # add table user_telegram_subscription
    # update_database(main_engine, query_tg_subscriptions)
    # # update table telegram_channel
    # update_tg_channels(main_engine)
    #
    # # create quote_group and quote_source tables
    # update_database(main_engine, query_quote_group)
    # update_database(main_engine, query_quote_source)
    # # update quote_group and quote_source tables
    # update_quote_group_table(main_engine)
    # update_quote_source_table(main_engine)

    # alter to quote_source table column
    alter_to_quote_source_column(main_engine)

    # create research_source table
    update_database(main_engine, query_research_source_table)
    # update research_source table
    update_research_source_table(main_engine)
