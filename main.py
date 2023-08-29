from module.mail_parse import ImapParse
from module.process_article import ArticleProcess
from config import mail_username, mail_password, mail_imap_server


CLIENT_FOLDER_DIR = "articles/client"
COMMODITY_FOLDER_DIR = "articles/commodity"
# TODO: timer


def parse_mail(type_of_article, folder_name):
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
    # get and download attachments
    filepath = imap_obj.get_and_download_attachment(folder_name)
    # close connection and log out
    imap_obj.close_connection()

    return filepath

def get_filepath():
    # TODO: нужно ?
    pass

# get articles
# client_filepath = parse_mail('client', CLIENT_FOLDER_DIR)
# commodity_filepath = parse_mail('commodity', COMMODITY_FOLDER_DIR)

# process articles
client_filepath = 'articles/client/Client news 28_08_2023.xlsx'
commodity_filepath = 'articles/commodity/Commodity news 28_08_2023.xlsx'
article_process_obj = ArticleProcess()
article_process_obj.set_df_article(client_filepath, commodity_filepath)
article_process_obj.process_articles()
article_process_obj.save_article()
