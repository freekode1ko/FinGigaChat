import datetime
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
    """
    Отправляет post запрос при помощи requests, совершает n-1 попыток с перехватом ошибки
    На n-ый раз делает запрос без перехвата ошибки, чтобы внешняя функция могла обработать ошибку
    """
    for _ in range(n - 1):
        try:
            return requests.post(**kwargs)
        except requests.ConnectTimeout as e:
            error_msg = 'Время ожидания запроса истекло при попытке подключения к удаленному серверу: %s'
            logger.error(error_msg, e)
            print(error_msg % e)
        except requests.Timeout as e:
            error_msg = 'Время ожидания запроса истекло: %s'
            logger.error(error_msg, e)
            print(error_msg % e)
        except requests.TooManyRedirects as e:
            error_msg = 'Слишком много перенаправлений: %s'
            logger.error(error_msg, e)
            print(error_msg % e)
        except requests.ConnectionError as e:
            error_msg = 'Возникла ошибка соединения: %s'
            logger.error(error_msg, e)
            print(error_msg % e)
        except requests.RequestException as e:
            error_msg = 'При обработке запроса произошло неоднозначное исключение: %s'
            logger.error(error_msg, e)
            print(error_msg % e)

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
                print('Старт получения новостей из тг-каналов из общего списка новостей')
                all_tg_articles_df = ap_obj_online.get_tg_articles(df_article)

                logger.info('Старт обработки новостей с помощью моделей')
                print('Старт обработки новостей с помощью моделей')
                df_article = ap_obj_online.throw_the_models(df_article)
                ap_obj_online.df_article = df_article
                ap_obj_online.drop_duplicate()
                ap_obj_online.make_text_sum()
                ap_obj_online.save_tables()

                saved_tg_df = ap_obj_online.get_tg_articles(ap_obj_online.df_article)
                df_article = ap_obj_online.update_tg_articles(saved_tg_df, all_tg_articles_df)

                if not df_article.empty:
                    ap_obj_online.df_article = df_article
                    ap_obj_online.make_text_sum()
                    ap_obj_online.save_tg_tables()
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
            start_time = time.time()
            now_str = datetime.datetime.now().strftime(config.BASE_DATETIME_FORMAT)
            start_msg = f'Запуск pipeline с новостями в {now_str}'
            logger.info(start_msg)
            print(start_msg)
            gotten_ids = regular_func()
            post_ids(gotten_ids)
            now_str = datetime.datetime.now().strftime(config.BASE_DATETIME_FORMAT)
            work_time = time.time() - start_time
            end_msg = f'Конец pipeline с новостями в {now_str}, завершено за {work_time:.3f} секунд'
            print(end_msg + '\nОжидайте\n')
            logger.info(end_msg)
            for i in range(PERIOD):
                time.sleep(3600)
                logger.debug('Ожидание: {}/{} часов'.format(i + 1, PERIOD))
                print('Ожидание: {}/{} часов'.format(i + 1, PERIOD))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(e)
        print(e)
