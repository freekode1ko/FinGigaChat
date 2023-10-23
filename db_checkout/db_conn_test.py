from sqlalchemy import create_engine, text
import pandas as pd

psql_engine = 'postgresql://testuser:12345678A@77.232.134.41:5432/users'
engine = create_engine(psql_engine)

query = ('CREATE TABLE IF NOT EXISTS public.whitelist ('
         'user_id integer NOT NULL, '
         'username text NOT NULL, '
         'email text, '
         'user_type text NOT NULL, '
         'user_status text NOT NULL, '
         'CONSTRAINT user_id_pkey PRIMARY KEY (user_id)) '
         'TABLESPACE pg_default;')
with engine.connect() as conn:
    conn.execute(text(query))
    conn.commit()
print('Table created')

query = "INSERT INTO public.test (name) VALUES ('test_name')"
with engine.connect() as conn:
    conn.execute(text(query))
    conn.commit()

df = pd.read_sql_query('select * from "test"', con=engine)
print(df)

query = "DROP TABLE IF EXISTS test CASCADE"
with engine.connect() as conn:
    conn.execute(text(query))
    conn.commit()
print('Table droped')
