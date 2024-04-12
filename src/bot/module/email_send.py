import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import smtplib


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

    def __enter__(self):
        self.server = smtplib.SMTP_SSL(self.host, self.port)
        self.server.login(self.login, self.password)

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

    def send_meeting(self, user_email: str, data: dict) -> None:
        """
        Отправка встречи пользователю.

        :param user_email: почта пользователя
        :param data: информация о встрече
        """

        r_n = "\r\n"
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
                         f"{r_n} ;CN={email_to};X-NUM-GUESTS=0:{r_n} mailto:{email_to}{r_n}")

        ical = (
            f"BEGIN:VCALENDAR{r_n}PRODID:pyICSParser{r_n}VERSION:2.0{r_n}CALSCALE:GREGORIAN{r_n}"
            f"METHOD:REQUEST{r_n}BEGIN:VEVENT{r_n}DTSTART:{meeting_start_frmt}{r_n}DTEND:{meeting_end_frmt}{r_n}"
            f"DTSTAMP:{dt_stamp}{r_n}ORGANIZER;CN=AI-помощник банкира:mailto:{self.BOT_NAME}{r_n} @mail.ru{r_n}"
            f"UID:FIXMEUID{dt_stamp}{r_n}"
            f"{email_to_frmt}CREATED:{dt_stamp}{r_n}DESCRIPTION: {meeting_description}{r_n}LAST-MODIFIED:{dt_stamp}{r_n}LOCATION:{r_n}"
            f"SEQUENCE:0{r_n}STATUS:CONFIRMED{r_n}"
            f"SUMMARY:{meeting_theme}{r_n}TRANSP:OPAQUE{r_n}END:VEVENT{r_n}END:VCALENDAR{r_n}"
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

        self.server.sendmail(self.EMAIL_FROM, email_to, msg.as_string())


