import datetime as dt
import time
import warnings
import requests

import pandas as pd

from module.article_process import ArticleProcess


PERIOD = dt.timedelta(hours=1, minutes=0)
FROM_TIME = ''
URL_TO_DB = 'http://gigaparsernews.ru:8000/get_articles/{date}:{hour}'  # TODO: перенести в конфиг
# TODO: проверить дайджесты
# TODO: не делать клин дата старым новостям, а брать из таблицы с импактами
# TODO: настроить фильтры на поли
# TODO: сделать парсинг каждые три часа
# TODO: утвердить метод сортировки, чтобы потом не нужно было переделывать
# TODO: сделать фильтр на "новость дополняется"


def get_period_article() -> pd.DataFrame:
    """ Get and save articles """
    df_article = pd.DataFrame()
    try:

        req = requests.get(URL_TO_DB)
        if req.status_code == 200:
            df_article = df_article.from_dict(req.json())
        else:
            print(f'{req.status_code} - status code while connect to database.')

    except ConnectionError:
        print('-- Error: Connection error.')

    return df_article


def regular_func():
    """ Processing for new articles """

    df_article = get_period_article()
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


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    regular_func()
    # while True:
    #     current_time = dt.datetime.now().time()
    #     current_time_timedelta = dt.timedelta(hours=current_time.hour, minutes=current_time.minute)
    #     delta_time = (PERIOD - current_time_timedelta).seconds
    #     print('time to wait', delta_time / 60)
    #     time.sleep(delta_time)
    #     regular_func()
    #     print('Wait next hour')
