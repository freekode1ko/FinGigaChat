import datetime as dt
import time
import warnings
import requests

import pandas as pd

from module.article_process import ArticleProcess


PERIOD = 3
URL_TO_PERIOD_DB = 'http://gigaparsernews.ru:8000/get_articles/{date}:{hour}'  # TODO: перенести в конфиг
URL_TO_ALL_DB = 'http://gigaparsernews.ru:8000/get_articles/all'  # TODO: перенести в конфиг
# TODO: сделать парсинг каждые три часа
# TODO: утвердить метод сортировки, чтобы потом не нужно было переделывать


def get_period_article(date: str = '0', hour: str = '0') -> pd.DataFrame:
    """ Get and save articles """
    df_article = pd.DataFrame()
    try:
        url = URL_TO_PERIOD_DB.format(date=date, hour=hour) if date != '0' else URL_TO_ALL_DB
        req = requests.get(url)
        if req.status_code == 200:
            df_article = df_article.from_dict(req.json())
        else:
            print(f'{req.status_code} - status code while connect to database.')
        print(f'url is {url}')

    except ConnectionError:
        print('-- Error: Connection error.')

    return df_article


def regular_func(date, hour):
    """ Processing for new articles """

    df_article = get_period_article(date, hour)
    article_flag = False if df_article.empty else True

    if article_flag:
        print(f'-- got {len(df_article)} articles')
        ap_obj_online = ArticleProcess()
        df_article = ap_obj_online.preprocess_article_online(df_article)
        print('-- go throw models')
        df_article = ap_obj_online.throw_the_models(df_article)
        ap_obj_online.df_article = df_article
        # ap_obj_online.df_article.to_excel('check online before dedup.xlsx', index=False)
        ap_obj_online.drop_duplicate()
        ap_obj_online.make_text_sum()
        # ap_obj_online.df_article.to_excel('check online after dedup.xlsx', index=False)
        ap_obj_online.save_tables()
        print('-- PROCESSED ARTICLES')
    else:
        print('-- DID NOT GET ARTICLES')


def get_datetime_of_last_article(date_, time_):
    df_article = get_period_article(date_, time_)
    max_timestamp = max(df_article['created_at'])
    datetime_ = pd.to_datetime(max_timestamp, unit='ms')
    df_article['created_at'] = df_article['created_at'].apply(lambda x: pd.to_datetime(x, unit='ms'))
    return datetime_


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    current_datetime = dt.datetime(year=2023, month=10, day=20, hour=0)  # МЕНЯТЬ ЕСЛИ ОСТАНОВИЛСЯ ПАРСИНГ
    try:
        while True:
            current_date_s = current_datetime.strftime('%d.%m.%y')
            current_hour_s = current_datetime.strftime('%H')
            print(current_date_s, current_hour_s)
            current_datetime = get_datetime_of_last_article(current_date_s, current_hour_s)
            print(current_datetime)

            # regular_func(current_date_s, current_hour_s)

            for i in range(PERIOD):
                # time.sleep(3600)
                time.sleep(5)
                print('In waiting: {}/3 hours'.format(i + 1))

    except KeyboardInterrupt:
        print('--- STOP TIMER:', current_datetime)
    except Exception as e:
        print(e)
        print('--- STOP TIMER:', current_datetime)
