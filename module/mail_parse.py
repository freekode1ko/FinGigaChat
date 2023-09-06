import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import os
import shutil


class ImapError(Exception):
    pass


def clear_dir(dir_path) -> None:
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


class ImapParse:
    """
    Class for parse messages from mail.
    """

    def __init__(self):
        self.imap = None
        self.msg = None

        self.client_box = "inbox/client_box"
        self.commodity_box = "inbox/commodity_box"

    def get_connection(self,  login, password, imap_server):
        self.imap = imaplib.IMAP4_SSL(imap_server)
        self.imap.login(login, password)

    def close_connection(self) -> None:
        """
        Close connection
        """
        self.imap.close()
        self.imap.logout()

    def get_index_of_new_msg(self, type_of_article: str) -> int:
        """
        Get index of the newest message from the email box.
        :param type_of_article: box from where we will get messages
        :return: index of the newest message
        """
        box = self.client_box if type_of_article == 'client' else self.commodity_box
        status, messages = self.imap.select(box)
        if status == 'OK':
            return int(messages[0])
        raise ImapError('Some error with get index message.')

    def get_msg(self, index_of_new_msg) -> email.message.Message:
        """
        Get the newest message and parse a bytes email into a message object.
        :param index_of_new_msg: index of the newest message
        :return: a message object
        """
        status_msg, msg = self.imap.fetch(str(index_of_new_msg), "(RFC822)")
        if status_msg == 'OK':
            return email.message_from_bytes(msg[0][1])
        raise ImapError('Some error with get new message.')

    def get_and_download_attachment(self, folder_name: str) -> str:
        """
        Get attachment in email message and download it in folder.
        :param folder_name: folder name where to save file
        :return: filename from email message
        """

        if self.msg.is_multipart():
            for part in self.msg.walk():
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" in content_disposition:
                    filename, encoding = decode_header(part.get_filename())[0]
                    if encoding is not None:
                        filename = filename.decode(encoding)
                    if filename and os.path.isdir(folder_name):
                        filepath = os.path.join(folder_name, filename)
                        clear_dir(folder_name)
                        open(filepath, "wb").write(part.get_payload(decode=True))
                        return filepath

        raise ImapError('Some error occurred while getting payload.')

    # def get_subject(self):
    #     """
    #     Get subject of the newest message
    #     :return: subject of the message
    #     """
    #     subject, encoding = decode_header(self.msg["Subject"])[0]
    #     if isinstance(subject, bytes):
    #         subject = subject.decode(encoding)
    #     return subject

    def get_date(self):
        """
        Get date of the newest message
        :return: subject of the message
        """
        date, encoding = decode_header(self.msg["Date"])[0]
        if isinstance(date, bytes):
            date = date.decode(encoding)
        return parsedate_to_datetime(date).date()
