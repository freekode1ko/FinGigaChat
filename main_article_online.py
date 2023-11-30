import time
import warnings
import requests
import json
from pathlib import Path

import pandas as pd

from module.article_process import ArticleProcess
from module import logger_base
from config import BASE_GIGAPARSER_URL


PERIOD = 3


def get_article() -> pd.DataFrame:
    """ Получение новостей """
    df_article = pd.DataFrame()
    try:
        url = BASE_GIGAPARSER_URL.format('get_articles/all')
        # url = 'http://gigaparsernews.ru:8000/get_articles/tg'
        req = requests.post(url)
        if req.status_code == 200:
            df_article = df_article.from_dict(req.json())
        else:
            logger.error(f'{req.status_code} - код ответа ')
            print(f'{req.status_code} - код ответа ')

    except ConnectionError:
        logger.error('Ошибка при получении новостей: ConnectionError')
        print('Ошибка при получении новостей: ConnectionError')

    return df_article


def regular_func():
    """ Обработка новых новостей """

    df_article = get_article()

    if not df_article.empty:
        try:
            print(f'Получено {len(df_article)} новостей')
            ap_obj_online = ArticleProcess(logger)
            df_article, ids = ap_obj_online.preprocess_article_online(df_article)
            if not df_article.empty:
                logger.info('Старт обработки новостей с помощью моделей')
                print('Старт обработки новостей с помощью моделей')
                df_article = ap_obj_online.throw_the_models(df_article)
                ap_obj_online.df_article = df_article
                ap_obj_online.drop_duplicate()
                ap_obj_online.make_text_sum()
                ap_obj_online.save_tables()
                print('Окончание обработки новостей с помощью моделей')
                logger.info('Окончание обработки новостей с помощью моделей')
            else:
                logger.error('Не были получены новости')
                print('Не были получены новости')
        except Exception as exp:
            logger.error(f'Ошибка при обработке новостей: {exp}')
            print(f'Ошибка при обработке новостей: {exp}')
            ids = json.dumps({'id': []})
    else:
        ids = json.dumps({'id': []})
        logger.error('Не были получены новости')
        print('Не были получены новости')

    return ids


def post_ids(ids):
    try:
        logger.debug('Отправка id обработанных новостей на сервер')
        requests.post(BASE_GIGAPARSER_URL.format('success_request'), json=ids)  # ids = {'id': [1,2,3...]}
    except Exception as e:
        print(f'Ошибка при отправке id обработанных новостей на сервер: {e}')
        logger.error(f'Ошибка при отправке id обработанных новостей на сервер: {e}')


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    # инициализируем логгер
    log_name = Path(__file__).stem
    logger = logger_base.logger(log_name)
    try:
        # запускаем периодическое получение/обработку новостей
        while True:
            logger.info('Запуск pipeline с новостями')
            print('Запуск pipeline с новостями')
            gotten_ids = regular_func()
            # post_ids(gotten_ids)
            print('Конец pipeline с новостями \nОжидайте\n')
            logger.info('Конец pipeline с новостями\n')
            for i in range(PERIOD):
                time.sleep(3600)
                logger.debug('Ожидание: {}/{} часов'.format(i + 1, PERIOD))
                print('Ожидание: {}/{} часов'.format(i + 1, PERIOD))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(e)
        print(e)
