import datetime as dt
import time
import warnings
import requests

import pandas as pd

from module.article_process import ArticleProcess


PERIOD = 3
URL_TO_PERIOD_DB = 'http://gigaparsernews.ru:8000/get_articles/{date}:{hour}'  # TODO: перенести в конфиг
URL_TO_ALL_DB = 'http://gigaparsernews.ru:8000/get_articles/all'  # TODO: перенести в конфиг
URL_POST_TO_DB = 'http://gigaparsernews.ru:8000/success_request'  # TODO: перенести в конфиг


def get_period_article(date: str = '0', hour: str = '0') -> pd.DataFrame:
    """ Get and save articles """
    df_article = pd.DataFrame()
    try:
        url = URL_TO_ALL_DB if date == '0' else URL_TO_PERIOD_DB.format(date=date, hour=hour)
        req = requests.get(url)
        if req.status_code == 200:
            df_article = df_article.from_dict(req.json())
        else:
            print(f'{req.status_code} - status code while connect to database.')
        print(f'url is {url}')

    except ConnectionError:
        print('-- Error: Connection error.')

    return df_article


def regular_func():
    """ Processing for new articles """

    df_article = get_period_article()
    article_flag = False if df_article.empty else True

    if article_flag:
        try:
            print(f'-- got {len(df_article)} articles')
            ap_obj_online = ArticleProcess()
            df_article, ids = ap_obj_online.preprocess_article_online(df_article)
            print('-- go throw models')
            df_article = ap_obj_online.throw_the_models(df_article)
            ap_obj_online.df_article = df_article
            # ap_obj_online.df_article.to_excel('check online before dedup.xlsx', index=False)
            ap_obj_online.drop_duplicate()
            ap_obj_online.make_text_sum()
            # ap_obj_online.df_article.to_excel('check online after dedup.xlsx', index=False)
            ap_obj_online.save_tables()
            print('-- PROCESSED ARTICLES')
        except Exception as e:
            print(e)
            ids = dict(id=[])
    else:
        ids = dict(id=[])
        print('-- DID NOT GET ARTICLES')

    return ids


def post_ids(ids):
    try:
        requests.post(URL_POST_TO_DB, json=ids)  # ids = {'id': [1,2,3...]}
    except Exception as e:
        print(e)


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    try:
        while True:
            gotten_ids = regular_func()
            post_ids(gotten_ids)
            for i in range(PERIOD):
                time.sleep(3600)
                print('In waiting: {}/{} hours'.format(i + 1, PERIOD))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
