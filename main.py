from module.mail_parse import ImapParse
from module.process_article import ArticleProcess
from config import mail_username, mail_password, mail_imap_server
import os
import time
import datetime as dt

CLIENT_FOLDER_DIR = "articles/client"
COMMODITY_FOLDER_DIR = "articles/commodity"
HOUR_TO_PARSE = dt.timedelta(hours=22, minutes=24)


def timer_parse() -> bool:
    count_of_attempt = 5
    for attempt in range(count_of_attempt):
        flag = work_with_article()
        if flag:
            print('GET ARTICLES')
            time.sleep(60)  # if pipe too fast
            return flag
        else:
            print('wait 3 min')
            time.sleep(1*60)

    print('DID NOT GET ARTICLES')
    return True

def parse_mail(imap_obj, type_of_article, folder_name):
    """
    Parse mail
    :param imap_obj: instance of ImapParse
    :param type_of_article: type of articles (client or commodity)
    :param folder_name: folder name where to save file
    :return: filename from mail message which was saved in directory.
    """

    # find index of the newest messages
    index_of_new_message = imap_obj.get_index_of_new_msg(type_of_article)
    # get message by index
    imap_obj.msg = imap_obj.get_msg(index_of_new_message)
    # get and download attachments
    filepath = imap_obj.get_and_download_attachment(folder_name)

    return filepath


def check_new_mail(imap_obj: ImapParse, type_of_article, folder_name):
    # get old filename
    old_filename = get_filename(folder_name)
    # find index of the newest messages
    index_of_new_message = imap_obj.get_index_of_new_msg(type_of_article)
    # get message by index
    imap_obj.msg = imap_obj.get_msg(index_of_new_message)
    # get subject of msg
    subject = imap_obj.get_subject()

    if subject == old_filename.split('.')[0]:
        return False
    else:
        return True


def get_filename(dir_path):
    list_of_files = [filename for filename in os.listdir(dir_path)]
    filename = '' if not list_of_files else list_of_files[0]
    return filename


def work_with_article() -> bool:
    """Parse mail"""
    # definition instance of ImapParse class
    imap_obj = ImapParse()
    # get connection and log in
    imap_obj.get_connection(mail_username, mail_password, mail_imap_server)
    # check for parse
    if check_new_mail(imap_obj, 'client', CLIENT_FOLDER_DIR) and check_new_mail(imap_obj, 'commodity',
                                                                                COMMODITY_FOLDER_DIR):
        # get articles
        client_filepath = parse_mail(imap_obj, 'client', CLIENT_FOLDER_DIR)
        commodity_filepath = parse_mail(imap_obj, 'commodity', COMMODITY_FOLDER_DIR)
        # close connection and log out
        imap_obj.close_connection()
        # process articles
        article_process_obj = ArticleProcess()
        article_process_obj.delete_old_article()
        # client
        df_client = article_process_obj.load_client_file(client_filepath)
        df_client = article_process_obj.throw_the_models('client', df_client)
        # commodity
        df_commodity = article_process_obj.load_commodity_file(commodity_filepath)
        df_commodity = article_process_obj.throw_the_models('commodity', df_commodity)
        # merge df
        article_process_obj.merge_client_commodity_article(df_client, df_commodity)
        article_process_obj.save_tables()
        return True
    else:
        imap_obj.close_connection()
        print('I did nothing')
        return False


if __name__ == '__main__':
    while True:
        current_time = dt.datetime.now().time()
        current_time_timedelta = dt.timedelta(hours=current_time.hour, minutes=current_time.minute)
        delta_time = (HOUR_TO_PARSE - current_time_timedelta).seconds
        print('begin wait in ', current_time_timedelta)
        print('time to wait', delta_time / 3600)
        time.sleep(delta_time)
        print('begin in ', current_time)
        flag = timer_parse()
        if flag:
            print('WAIT NEXT DAY')


