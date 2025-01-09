import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import aiosmtplib


class SmtpSend:
    """Класс для работы с SMTP почтового сервера, для отправки писем"""

    BOT_NAME = 'ai-helper'
    EMAIL_FROM = "ai-helper <ai-helper@mail.ru>"

    def __init__(self, login: str, password: str, host: str, port: int):
        self.server = None
        self.login = login
        self.password = password
        self.host = host
        self.port = port

    async def __aenter__(self):
        self.server = aiosmtplib.SMTP(hostname=self.host, port=self.port, use_tls=True)
        await self.server.connect()
        await self.server.login(self.login, self.password)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.server.quit()

    async def send_msg(self, sender: str, recipient: str, subject: str, message: str):
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
        await self.server.sendmail(sender, recipient, mail)

    async def send_meeting(self, user_email: str, data: dict) -> None:
        """
        Отправка встречи пользователю.

        :param user_email: почта пользователя
        :param data: информация о встрече
        """

        date_format = '%Y%m%dT%H%M%S%Z'
        cur_date = datetime.datetime.now()
        dt_stamp = cur_date.strftime(date_format)

        email_to = user_email
        meeting_start = data.get('date_start')
        meeting_end = data.get('date_end')

        # user_timezone = data.get('timezone')
        # meeting_start += datetime.timedelta(hours=user_timezone)
        # meeting_end += datetime.timedelta(hours=user_timezone)

        meeting_start_frmt = meeting_start.strftime(date_format)
        meeting_end_frmt = meeting_end.strftime(date_format)

        meeting_theme = data.get('theme')
        meeting_description = data.get("description")

        email_to_frmt = (f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-    PARTICIPANT;PARTSTAT=ACCEPTED;RSVP=TRUE"
                         f"\r\n ;CN={email_to};X-NUM-GUESTS=0:\r\n mailto:{email_to}\r\n")

        ical = (
            f"BEGIN:VCALENDAR\r\nPRODID:pyICSParser\r\nVERSION:2.0\r\nCALSCALE:GREGORIAN\r\n"
            f"METHOD:REQUEST\r\nBEGIN:VEVENT\r\nDTSTART:{meeting_start_frmt}\r\nDTEND:{meeting_end_frmt}\r\n"
            f"DTSTAMP:{dt_stamp}\r\nORGANIZER;CN=AI-помощник банкира:mailto:{self.BOT_NAME}\r\n @mail.ru\r\n"
            f"UID:FIXMEUID{dt_stamp}\r\n"
            f"{email_to_frmt}CREATED:{dt_stamp}\r\nDESCRIPTION: {meeting_description}\r\nLAST-MODIFIED:{dt_stamp}\r\n"
            f"LOCATION:\r\nSEQUENCE:0\r\nSTATUS:CONFIRMED\r\n"
            f"SUMMARY:{meeting_theme}\r\nTRANSP:OPAQUE\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n"
        )

        eml_body = meeting_description
        msg = MIMEMultipart('mixed')
        msg['Date'] = formatdate(localtime=True)
        msg['Reply-To'] = self.EMAIL_FROM
        msg['Subject'] = meeting_theme
        msg['From'] = self.EMAIL_FROM
        msg['To'] = email_to

        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)
        ical_atch = MIMEBase('application/ics', ' ;name="%s"' % ("invite.ics"))
        ical_atch.set_payload(ical)
        encoders.encode_base64(ical_atch)
        ical_atch.add_header('Content-Disposition', 'attachment; filename="%s"' % ("invite.ics"))
        eml_atch = MIMEText('', 'plain')
        encoders.encode_base64(eml_atch)
        eml_atch.add_header('Content-Transfer-Encoding', "")

        part_email = MIMEText(eml_body, "html")
        msg_alternative.attach(part_email)
        msg_alternative.attach(MIMEText(ical, 'calendar;method=REQUEST'))

        if self.server is None:
            raise ConnectionError('Сервер не определен')

        await self.server.sendmail(self.EMAIL_FROM, email_to, msg.as_string())
