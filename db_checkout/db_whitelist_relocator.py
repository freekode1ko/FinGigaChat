import pandas as pd
from sqlalchemy import create_engine, text

print('Connecting to NEW database...')
psql_engine_new = 'postgresql://testuser:12345678A@77.232.134.41:5432/users'
engine_new = create_engine(psql_engine_new)
print('Connection to NEW database is established')

print('Connecting to OLD database...')
psql_engine_old = 'postgresql://bot:12345@217.18.62.123:5432/users'
engine_old = create_engine(psql_engine_old)
print('Connection to OLD database is established')

old_whitelist = pd.read_sql_query('select * from "whitelist"', con=engine_old)
print(old_whitelist)

query = (
    'CREATE TABLE IF NOT EXISTS public.whitelist ('
    'user_id integer NOT NULL, '
    'username text NOT NULL, '
    'email text, '
    'user_type text NOT NULL, '
    'user_status text NOT NULL, '
    'CONSTRAINT user_id_pkey PRIMARY KEY (user_id)) '
    'TABLESPACE pg_default;'
)
with engine_new.connect() as conn:
    conn.execute(text(query))
    conn.commit()
print('Table created in NEW database')

old_whitelist.to_sql('whitelist', con=engine_new, if_exists='replace', index=False)
print('Users from PROM successful postponed')
