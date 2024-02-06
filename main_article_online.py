import json
import time
import warnings
from pathlib import Path

import pandas as pd
import requests

import config
from config import BASE_GIGAPARSER_URL
from module.article_process import ArticleProcess
from module.logger_base import selector_logger
from utils import sentry

PERIOD = 1


def try_post_n_times(n: int, **kwargs) -> requests.Response:
    """Отправляет post запрос при помощи requests, совершает n-1 попыток с перехватом ошибки"""
    for _ in range(n - 1):
        try:
            return requests.post(**kwargs)
        except requests.ConnectTimeout as e:
            error_msg = f'Время ожидания запроса истекло при попытке подключения к удаленному серверу: {e}'
            logger.error(error_msg)
            print(error_msg)
        except requests.Timeout as e:
            error_msg = f'Время ожидания запроса истекло: {e}'
            logger.error(error_msg)
            print(error_msg)
        except requests.TooManyRedirects as e:
            error_msg = f'Слишком много перенаправлений: {e}'
            logger.error(error_msg)
            print(error_msg)
        except requests.ConnectionError as e:
            error_msg = f'Возникла ошибка соединения: {e}'
            logger.error(error_msg)
            print(error_msg)
        except requests.RequestException as e:
            error_msg = f'При обработке запроса произошло неоднозначное исключение: {e}'
            logger.error(error_msg)
            print(error_msg)

        time.sleep(config.POST_TO_GIGAPARSER_SLEEP_AFTER_ERROR)

    return requests.post(**kwargs)


def get_article() -> pd.DataFrame:
    """Получение новостей"""
    df_article = pd.DataFrame()
    try:
        url = BASE_GIGAPARSER_URL.format('get_articles/all')
        req = try_post_n_times(config.POST_TO_GIGAPARSER_ATTEMPTS, url=url, timeout=config.POST_TO_GIGAPARSER_TIMEOUT)
        if req.status_code == 200:
            df_article = df_article.from_dict(req.json())
        else:
            logger.error(f'{req.status_code} - код ответа ')
            print(f'{req.status_code} - код ответа ')

    except ConnectionError:
        logger.error('Ошибка при получении новостей: ConnectionError')
        print('Ошибка при получении новостей: ConnectionError')

    except Exception as e:
        logger.error('Ошибка при получении новостей: %s', e)
        print(f'Ошибка при получении новостей: {e}')

    return df_article


def regular_func():
    """Обработка новых новостей"""

    df_article = get_article()

    if not df_article.empty:
        try:
            logger.info(f'Получено {len(df_article)} новостей')
            print(f'Получено {len(df_article)} новостей')
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
        # ids = {'id': [1,2,3...]}
        try_post_n_times(
            config.POST_TO_GIGAPARSER_ATTEMPTS,
            url=BASE_GIGAPARSER_URL.format('success_request'),
            json=ids,
            timeout=config.POST_TO_GIGAPARSER_TIMEOUT
        )
    except Exception as e:
        print(f'Ошибка при отправке id обработанных новостей на сервер: {e}')
        logger.error('Ошибка при отправке id обработанных новостей на сервер: %s', e)


if __name__ == '__main__':
    sentry.init_sentry(dsn=config.SENTRY_NEWS_PARSER_DSN)
    warnings.filterwarnings('ignore')
    # инициализируем логгер
    log_name = Path(__file__).stem
    logger = selector_logger(log_name)
    try:
        # запускаем периодическое получение/обработку новостей
        ap_obj_online = ArticleProcess(logger)
        while True:
            logger.info('Запуск pipeline с новостями')
            print('Запуск pipeline с новостями')
            gotten_ids = regular_func()
            post_ids(gotten_ids)
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
