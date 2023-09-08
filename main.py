import datetime as dt
import time

import pandas as pd

from module.process_article import ArticleProcess
from module.mail_parse import ImapParse
from config import mail_username, mail_password, mail_imap_server

CLIENT_FOLDER_DIR = "articles/client"
COMMODITY_FOLDER_DIR = "articles/commodity"
HOUR_TO_PARSE = dt.timedelta(hours=10, minutes=7)


def imap_func(type_of_article, folder_name):
    """
    Parse mail
    :param type_of_article: type of articles (client or commodity)
    :param folder_name: folder name where to save file
    :return: filename from mail message which was saved in directory.
    """
    # definition instance of ImapParse class
    imap_obj = ImapParse()
    # get connection and log in
    imap_obj.get_connection(mail_username, mail_password, mail_imap_server)
    # find index of the newest messages
    index_of_new_message = imap_obj.get_index_of_new_msg(type_of_article)
    # get message by index
    imap_obj.msg = imap_obj.get_msg(index_of_new_message)
    # get date of msg
    date_msg = imap_obj.get_date()

    if date_msg == dt.datetime.now().date():
        # get and download attachments
        filepath = imap_obj.get_and_download_attachment(folder_name)
    else:
        filepath = None

    # close connection and log out
    imap_obj.close_connection()
    time.sleep(10)

    return filepath


def model_func(ap_obj: ArticleProcess, type_of_article, folder_dir):

    filepath = imap_func(type_of_article, folder_dir)
    if filepath is not None:
        df = ap_obj.load_client_file(filepath) if type_of_article == 'client' else ap_obj.load_commodity_file(filepath)
        df = ap_obj.throw_the_models(type_of_article, df)
        df.to_csv(filepath, index=False)
        return True, filepath
    else:
        return False, None


def daily_func():

    # delete old articles from database
    ap_obj = ArticleProcess()
    ap_obj.delete_old_article()

    client_flag = commodity_flag = False
    client_filepath = commodity_filepath = None

    count_of_attempt = 5
    for attempt in range(count_of_attempt):

        if not client_flag:
            client_flag, client_filepath = model_func(ap_obj, 'client', CLIENT_FOLDER_DIR)

        if not commodity_flag:
            commodity_flag, commodity_filepath = model_func(ap_obj, 'commodity', COMMODITY_FOLDER_DIR)

        if client_flag and commodity_flag:
            print('GOT ARTICLES')
            break
        else:
            print('wait 10 min')
            time.sleep(10 * 60)

    df_client = pd.read_csv(client_filepath, index_col=False) if client_flag else (
        pd.DataFrame([], columns=['link', 'title', 'date', 'text', 'text_sum', 'client', 'client_score']))

    df_commodity = pd.read_csv(commodity_filepath, index_col=False) if commodity_flag else (
        pd.DataFrame([], columns=['link', 'title', 'date', 'text', 'commodity', 'commodity_score']))

    if client_flag or commodity_flag:
        ap_obj.merge_client_commodity_article(df_client, df_commodity)
        ap_obj.save_tables()
        if client_flag and commodity_flag:
            print('PROCESSED ARTICLES')
        elif client_flag:
            print('PROCESSED ONLY CLIENT ARTICLES')
        else:
            print('PROCESSED ONLY COMMODITY ARTICLES')
    else:
        print('DID NOT GET ARTICLES')

    time.sleep(60)  # if pipe too fast


if __name__ == '__main__':
    while True:
        current_time = dt.datetime.now().time()
        current_time_timedelta = dt.timedelta(hours=current_time.hour, minutes=current_time.minute)
        delta_time = (HOUR_TO_PARSE - current_time_timedelta).seconds
        print('time to wait', delta_time / 60)
        time.sleep(delta_time)
        daily_func()
        print('Wait next day')
