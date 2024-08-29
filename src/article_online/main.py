"""Точка входа для сервиса обработки новостей от GigaParsers."""
import datetime
import json
import time
import warnings

import pandas as pd
import requests

from configs import config
from configs.config import BASE_GIGAPARSER_URL
from log import sentry
from log.logger_base import selector_logger
from module.article_process import ArticleProcess

MAX_NEWS_BATCH_SIZE = 1000
MINUTE = 60
MINUTES_TO_SLEEP = 20


def try_post_n_times(n: int, **kwargs) -> requests.Response:
    """
    Отправляет post запрос при помощи requests, совершает n-1 попыток с перехватом ошибки.

    На n-ый раз делает запрос без перехвата ошибки, чтобы внешняя функция могла обработать ошибку
    :param n:       Количество попыток.
    :param kwargs:  Параметры для POST запроса.
    :return:        Ответ на POST запрос или исключение.
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

        time.sleep(config.POST_TO_SERVICE_SLEEP_AFTER_ERROR)

    return requests.post(**kwargs)


def get_article() -> pd.DataFrame:
    """
    Получить новости.

    :return: Датафрейм с новостями и их атрибутами.
    """
    df_article = pd.DataFrame()
    try:
        url = BASE_GIGAPARSER_URL.format(f'get_articles/all?stand={config.STAND}')
        req = try_post_n_times(config.POST_TO_SERVICE_ATTEMPTS, url=url, timeout=config.POST_TO_GIGAPARSER_TIMEOUT)
        if req.status_code == 200:
            df_article = df_article.from_dict(req.json())
        else:
            logger.error(f'{req.status_code} - код ответа ')
            print(f'{req.status_code} - код ответа ')

    except Exception as e:
        logger.error('Ошибка при получении новостей: %s', e)
        print(f'Ошибка при получении новостей: {e}')

    return df_article


def regular_func() -> tuple[str, list, list]:
    """
    Обработать новые новости.

    :return: ID полученных новостей,
             Список ссылок на новые новости о клиентах/коммодах,
             Список ссылок на тг новости об отраслях.
    """
    subject_links, tg_links = [], []
    df_article = get_article()
    logger.info(f'Получено всего {len(df_article)} новостей')
    print(f'Получено всего {len(df_article)} новостей')
    # Берем первую тысячу новостей для обработки
    df_article = df_article[:MAX_NEWS_BATCH_SIZE]

    if not df_article.empty:
        try:
            logger.info(f'На обработку получено {len(df_article)} новостей')
            print(f'На обработку получено {len(df_article)} новостей')
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
                try:
                    ap_obj_online.apply_gigachat_filtering()
                except Exception as e:
                    logger.error('Ошибка при фильтрации новостей с помощью ГигаЧата: %s', e)
                ap_obj_online.remove_html_tags()
                subject_links = ap_obj_online.save_tables()

                logger.info('Старт обработки телеграм новостей')
                print('Старт обработки телеграм новостей')
                # сохраняем все тг новости без фильтраций
                saved_tg_df = ap_obj_online.get_tg_articles(ap_obj_online.df_article)
                df_article = ap_obj_online.update_tg_articles(saved_tg_df, all_tg_articles_df)

                if not df_article.empty:
                    ap_obj_online.df_article = df_article
                    ap_obj_online.make_text_sum()
                    ap_obj_online.remove_html_tags()
                    tg_links = ap_obj_online.save_tg_tables()

                print('Окончание обработки новостей с помощью моделей')
                logger.info('Окончание обработки новостей с помощью моделей')
            else:
                logger.error('Не были получены новости')
                print('Не были получены новости')
        except Exception as exp:
            logger.error(f'Ошибка при обработке новостей: {exp}')
            print(f'Ошибка при обработке новостей: {exp}')
            ids = json.dumps({'id': []})
            subject_links, tg_links = [], []
    else:
        ids = json.dumps({'id': []})
        subject_links, tg_links = [], []
        logger.error('Не были получены новости')
        print('Не были получены новости')

    return ids, subject_links, tg_links


def post_ids(ids: str) -> None:
    """
    Отправить id обработанных новостей GigaParsers.

    :param ids: Json из списка id обработанных новостей.
    """
    try:
        logger.debug('Отправка id обработанных новостей на сервер')
        # ids = {'id': [1,2,3...]}
        try_post_n_times(
            config.POST_TO_SERVICE_ATTEMPTS,
            url=BASE_GIGAPARSER_URL.format(f'success_request?stand={config.STAND}'),
            json=ids,
            timeout=config.POST_TO_GIGAPARSER_TIMEOUT,
        )
    except Exception as e:
        print(f'Ошибка при отправке id обработанных новостей на сервер: {e}')
        logger.error('Ошибка при отправке id обработанных новостей на сервер: %s', e)


def post_new_links(subject_links: list, tg_links: list) -> None:
    """
    Отправить ссылки на сохраненные новости в RAG по новостям.

    :param subject_links: Ссылки на новости по клиентам/коммодам.
    :param tg_links:      Ссылки на новости из Telegram (по индустриям и общим каналам).
    """
    logger.debug('Отправка ссылок сохраненных новостей на сервер')
    links_dict = {
        'subject_links': subject_links,  # ссылки на новости по клиентам и коммодам
        'tg_links': tg_links,  # ссылки на новости из тг каналов
    }
    try:
        response = try_post_n_times(
            config.POST_TO_SERVICE_ATTEMPTS,
            url=config.BASE_QABANKER_URL.format('articles'),
            json=links_dict,
            timeout=config.POST_TO_SERVICE_TIMEOUT,
        )
        logger.info(response.json()['message'])
    except Exception as e:
        print(f'Ошибка при отправке ссылок новостей в QABanker: {e}')
        logger.error('Ошибка при отправке ссылок новостей в QABanker:: %s', e)


if __name__ == '__main__':
    sentry.init_sentry(dsn=config.SENTRY_NEWS_PARSER_DSN)
    warnings.filterwarnings('ignore')
    # инициализируем логгер
    logger = selector_logger(config.log_file)
    try:
        # запускаем периодическое получение/обработку новостей
        ap_obj_online = ArticleProcess(logger)
        while True:
            start_time = time.time()
            now_str = datetime.datetime.now().strftime(config.BASE_DATETIME_FORMAT)
            start_msg = f'Запуск pipeline с новостями в {now_str}'
            logger.info(start_msg)
            print(start_msg)

            gotten_ids, new_subject_links, new_tg_links = regular_func()
            # post_ids(gotten_ids)  # отправка giga parsers полученных айди
            if not config.DEBUG:
                post_new_links(new_subject_links, new_tg_links)  # отправка qa banker ссылок сохраненных новостей

            now_str = datetime.datetime.now().strftime(config.BASE_DATETIME_FORMAT)
            work_time = time.time() - start_time
            end_msg = f'Конец pipeline с новостями в {now_str}, завершено за {work_time:.3f} секунд'
            print(end_msg + '\nОжидайте\n')
            logger.info(end_msg)
            for i in range(MINUTES_TO_SLEEP):
                time.sleep(MINUTE)
                logger.debug('Ожидание: {}/{} минут'.format(i + 1, MINUTES_TO_SLEEP))
                print('Ожидание: {}/{} минут'.format(i + 1, MINUTES_TO_SLEEP))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(e)
        print(e)
