"""Работа с SMTP"""
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Sequence

from typing_extensions import Self


class SmtpSend:
    """Класс для работы с SMTP почтового сервера, для отправки писем"""

    def __init__(self, login: str, password: str, host: str, port: int) -> None:
        """Конструктор"""
        self.server = None
        self.login = login
        self.password = password
        self.host = host
        self.port = port

    def __enter__(self) -> Self:
        """Контекстный менеджер для отправления писем"""
        self.server = smtplib.SMTP_SSL(self.host, self.port)
        self.server.login(self.login, self.password)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Контекстный менеджер для отправления писем"""
        self.server.close()

    def send_msg(
            self,
            sender: str,
            recipients: str | Sequence[str],
            subject: str,
            message: str,
            files: list[Path] = None,
    ) -> None:
        """
        Отправка письма через SMTP

        :param sender: EMAIL адрес с которого будет происходить отправка
        :param recipients: EMAIL адрес получателя письма
        :param subject: Тема письма
        :param message: Текст письма
        :param files: Файлы, которые надо прикрепить к письму
        """
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipients if isinstance(recipients, str) else ', '.join(recipients)
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        for f in files or []:
            with open(f, 'rb') as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=f.name,
                )
            # After the file is closed
            part['Content-Disposition'] = f'attachment; filename="{f.name}"'
            msg.attach(part)

        mail = msg.as_string()
        self.server.sendmail(sender, recipients, mail)
