from sqlalchemy import create_engine, text
import pandas as pd

psql_engine = 'postgresql://testuser:12345678A@77.232.134.41:5432/users'
engine = create_engine(psql_engine)

query = ('CREATE TABLE IF NOT EXISTS public.test '
         '(id integer NOT NULL GENERATED ALWAYS AS IDENTITY '
         '( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ), '
         'name text NOT NULL, CONSTRAINT test_pkey PRIMARY KEY (id)) '
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
