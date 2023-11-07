import time
import warnings
import requests
import json

import pandas as pd

from module.article_process import ArticleProcess
from config import BASE_GIGAPARSER_URL


PERIOD = 3


def get_article() -> pd.DataFrame:
    """ Get and save articles """
    df_article = pd.DataFrame()
    try:
        url = BASE_GIGAPARSER_URL.format('get_articles/all')
        req = requests.post(url)
        if req.status_code == 200:
            df_article = df_article.from_dict(req.json())
        else:
            print(f'{req.status_code} - status code while connect to database.')

    except ConnectionError:
        print('-- Error: Connection error.')

    return df_article


def regular_func():
    """ Processing for new articles """

    df_article = get_article()

    if not df_article.empty:
        try:
            print(f'-- got {len(df_article)} articles')
            ap_obj_online = ArticleProcess()
            df_article, ids = ap_obj_online.preprocess_article_online(df_article)
            if not df_article.empty:
                print('-- go throw models')
                df_article = ap_obj_online.throw_the_models(df_article)
                ap_obj_online.df_article = df_article
                ap_obj_online.drop_duplicate()
                ap_obj_online.make_text_sum()
                ap_obj_online.save_tables()
                print('-- PROCESSED ARTICLES')
            else:
                print('-- DID NOT GET ARTICLES')
        except Exception as exp:
            print(exp)
            ids = json.dumps({'id': []})
    else:
        ids = json.dumps({'id': []})
        print('-- DID NOT GET ARTICLES')

    return ids


def post_ids(ids):
    try:
        print('-- do post request with ids')
        requests.post(BASE_GIGAPARSER_URL.format('success_request'), json=ids)  # ids = {'id': [1,2,3...]}
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
