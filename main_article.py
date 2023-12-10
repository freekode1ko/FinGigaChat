import datetime as dt
import time
import warnings
from pathlib import Path

import pandas as pd

from module.article_process import ArticleProcess
from module.mail_parse import ImapParse
from module.logger_base import selector_logger
from config import mail_username, mail_password, mail_imap_server

CLIENT_FOLDER_DIR = "data/articles/client"
COMMODITY_FOLDER_DIR = "data/articles/commodity"
HOUR_TO_PARSE = dt.timedelta(hours=3, minutes=30)


def imap_func(type_of_article, folder_name):
    """
    Parse mail
    :param type_of_article: type of articles (client or commodity)
    :param folder_name: folder name where to save file
    :return: filename from mail message which was saved in directory.
    """

    imap_obj = ImapParse()
    imap_obj.get_connection(mail_username, mail_password, mail_imap_server)
    index_of_new_message = imap_obj.get_index_of_new_msg(type_of_article)
    imap_obj.msg = imap_obj.get_msg(index_of_new_message)
    date_msg = imap_obj.get_date()

    if date_msg == dt.datetime.now().date():
        filepath = imap_obj.get_and_download_attachment(folder_name)
    else:
        filepath = None

    imap_obj.close_connection()
    time.sleep(10)

    return filepath


def model_func(ap_obj: ArticleProcess, type_of_article, folder_dir):

    filepath = imap_func(type_of_article, folder_dir)
    if filepath:
        logger.info(f'Скачен файл: {filepath}')
        print(f'Скачен файл: {filepath}')
        df = ap_obj.load_file(filepath, type_of_article)
        if not df.empty:
            logger.info('Старт обработки новостей с помощью моделей')
            print('Старт обработки новостей с помощью моделей')
            df = ap_obj.throw_the_models(df, type_of_article, online_flag=False)
            print('Окончание обработки новостей с помощью моделей')
            logger.info('Окончание обработки новостей с помощью моделей')
        else:
            logger.warning(f'{filepath} - пустой')
            print(f'{filepath} - пустой')
            df[['text_sum', f'{type_of_article}_score', 'cleaned_data', f'{type_of_article}_impact']] = None
        logger.info('Сохранение новостей в csv файл')
        df.to_csv(filepath, index=False)
        return True, filepath
    else:
        return False, None


def daily_func():

    ap_obj = ArticleProcess(logger)
    client_flag = commodity_flag = False
    client_filepath = commodity_filepath = ''
    count_of_attempt = 9
    for attempt in range(count_of_attempt):

        if not client_flag:
            client_flag, client_filepath = model_func(ap_obj, 'client', CLIENT_FOLDER_DIR)

        if not commodity_flag:
            commodity_flag, commodity_filepath = model_func(ap_obj, 'commodity', COMMODITY_FOLDER_DIR)

        if client_flag and commodity_flag:
            break
        else:
            logger.info('Ожидание 20 минут')
            time.sleep(20 * 60)

    df_client = pd.read_csv(client_filepath, index_col=False) if client_flag else (
        pd.DataFrame([], columns=['link', 'title', 'date', 'text', 'text_sum', 'client', 'client_impact',
                                  'client_score', 'cleaned_data']))

    df_commodity = pd.read_csv(commodity_filepath, index_col=False) if commodity_flag else (
        pd.DataFrame([], columns=['link', 'title', 'date', 'text', 'text_sum', 'commodity', 'commodity_impact',
                                  'commodity_score', 'cleaned_data']))

    if client_flag or commodity_flag:
        logger.info(f'Получение новостей по клиентам - {client_flag}')
        logger.info(f'Получение новостей по клиентам - {commodity_flag}')
        if not df_client.empty or not df_commodity.empty:
            ap_obj.merge_client_commodity_article(df_client, df_commodity)
            ap_obj.drop_duplicate()
            ap_obj.make_text_sum()
            ap_obj.save_tables()
        else:
            logger.warning('Таблицы с новостями пустые')
            print('Таблицы с новостями пустые')
        if client_flag and commodity_flag:
            logger.info('Новости о клиентах и товарах обработаны')
            print('Новости о клиентах и товарах обработаны')
        elif client_flag:
            logger.warning('Обработаны только новости о клиентах')
            print('Обработаны только новости о клиентах')
        else:
            logger.warning('Обработаны только новости о товарах')
            print('Обработаны только новости о товарах')
    else:
        logger.error('Не были получены новости')
        print('Не были получены новости')

    # delete old articles from database
    # TODO: перед запуском еще раз внимательно проверить
    # ap_obj.delete_old_article()


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    # инициализируем логгер
    log_name = Path(__file__).stem
    logger = selector_logger(log_name)
    # запускаем ежедневное получение/обработку новостей от полианалиста
    while True:
        # высчитываем время ожидания
        current_time = dt.datetime.now().time()
        current_time_timedelta = dt.timedelta(hours=current_time.hour, minutes=current_time.minute)
        delta_time = (HOUR_TO_PARSE - current_time_timedelta).seconds
        logger.debug(f'Время ожидания в часах - {delta_time / 3600}')
        time.sleep(delta_time)

        logger.info('Запуск pipeline с новостями от полианалиста')
        print('Запуск pipeline с новостями от полианалиста')
        daily_func()
        print('Конец pipeline с новостями от полианалиста\nОжидайте следующий день\n')
        logger.info('Конец pipeline с новостями от полианалиста\n')
