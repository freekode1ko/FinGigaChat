from module.mail_parse import ImapParse
from module.process_article import ArticleProcess
from config import mail_username, mail_password, mail_imap_server
import os


CLIENT_FOLDER_DIR = "articles/client"
COMMODITY_FOLDER_DIR = "articles/commodity"
# TODO: timer


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


def main():

    """Parse mail"""
    # TODO: timer, check for delete, check for path
    # definition instance of ImapParse class
    imap_obj = ImapParse()
    # get connection and log in
    imap_obj.get_connection(mail_username, mail_password, mail_imap_server)
    # check for parse
    if check_new_mail(imap_obj, 'client', CLIENT_FOLDER_DIR) and check_new_mail(imap_obj, 'commodity', COMMODITY_FOLDER_DIR):
        # get articles
        client_filepath = parse_mail(imap_obj, 'client', CLIENT_FOLDER_DIR)
        commodity_filepath = parse_mail(imap_obj, 'commodity', COMMODITY_FOLDER_DIR)
        # close connection and log out
        imap_obj.close_connection()
        # process articles
        article_process_obj = ArticleProcess()
        article_process_obj.set_df_article(client_filepath, commodity_filepath)
        article_process_obj.process_articles()
        article_process_obj.save_tables()
    else:
        imap_obj.close_connection()
        print('I did nothing')


if __name__ == '__main__':
    main()