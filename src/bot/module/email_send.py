from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


class SmtpSend:
    """Класс для работы с SMTP почтового сервера, для отправки писем"""

    def __init__(self, login: str, password: str, host: str, port: int):
        self.server = None
        self.login = login
        self.password = password
        self.host = host
        self.port = port

    def __enter__(self):
        self.server = smtplib.SMTP_SSL(self.host, self.port)
        self.server.login(self.login, self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server.close()

    def send_msg(self, sender: str, recipient: str, subject: str, message: str):
        """
        Отправка письма через SMTP

        :param sender: EMAIL адрес с которого будет происходить отправка
        :param recipient: EMAIL адрес получателя письма
        :param subject: Тема письма
        :param message: Текст письма
        """
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))
        mail = msg.as_string()
        self.server.sendmail(sender, recipient, mail)
