import ssl

from aiogram import Bot
import dramatiq
from dramatiq.middleware.asyncio import AsyncIO
from dramatiq.brokers.redis import RedisBroker
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import (
    MAIL_RU_LOGIN,
    MAIL_RU_PASSWORD,
    MAIL_SMTP_PORT,
    MAIL_SMTP_SERVER,
    MEETING_PAGES
)
from utils.email_send import SmtpSend
from db.meeting import *
from utils.utils import format_date, reformat_data
from config import STATIC_CHAIN_PATH, STATIC_KEY_PATH, BOT_API_TOKEN, REMEMBER_TIME

# from schedular import send_schedular_new_data


app = FastAPI()
bot = Bot(BOT_API_TOKEN)

broker = RedisBroker(url='redis://127.0.0.1', middleware=[AsyncIO()])
broker.flush_all()
dramatiq.set_broker(broker=broker)


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(STATIC_CHAIN_PATH, keyfile=STATIC_KEY_PATH)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[MEETING_PAGES],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@dramatiq.actor
async def send_notification(user_id: int, meeting_theme: str, msg: str):
    msg = msg.format(meeting_theme=meeting_theme)
    await bot.send_message(user_id, text=f'<b>Напоминание:</b>\n{msg}', parse_mode='HTML')


@app.get("/meeting/show/{user_id}")
def read_root(user_id):
    if user_id is not None:
        meetings = get_user_meetings(user_id)
        meetings = format_date(meetings)
        return JSONResponse(meetings)
    else:
        return 'Отсутствует User ID.'


@app.get('/meeting/create')
def create_meeting(user_id, theme, date_start, date_end, description, timezone):
    data = {
        'user_id': user_id,
        'theme': theme,
        'date_start': date_start,
        'date_end': date_end,
        'description': description,
        'timezone': timezone
    }
    data = reformat_data(data)
    add_meeting(data)
    # send_schedular_new_data(data)  # напоминания

    user_email = get_user_email(user_id=user_id)
    with SmtpSend(MAIL_RU_LOGIN, MAIL_RU_PASSWORD, MAIL_SMTP_SERVER, MAIL_SMTP_PORT) as smtp_email:
        smtp_email.send_meeting(user_email, data)

    return 'OK'


def send_all_meetings():

    meetings = get_user_meetings_for_notification()
    for rem_time_dict in REMEMBER_TIME.values():
        for meeting in meetings:
            cur_time = dt.datetime.now()
            rem_time = rem_time_dict['minutes']
            dt_notification = meeting['date_start'] + dt.timedelta(hours=meeting['timezone']) - dt.timedelta(minutes=rem_time)
            if dt_notification < cur_time:
                print(meeting['theme'], '-', 'no')
                continue
            delay_val = dt_notification - cur_time
            print(meeting['theme'], '-', 'yes', meeting['theme'], 'in', dt_notification)

            send_notification.send_with_options(
                args=(meeting['user_id'], meeting['theme'], rem_time_dict['msg']),
                delay=delay_val
            )

'''
def send_schedular_new_data(meeting: dict[str, Any]):

    for rem_time_dict in REMEMBER_TIME.values():
        cur_time = dt.datetime.now()
        rem_time = rem_time_dict['minutes']
        dt_notification = meeting['date_start'] + dt.timedelta(hours=meeting['timezone']) - dt.timedelta(minutes=rem_time)
        if dt_notification < cur_time:
            print(meeting['theme'], '-', 'no')
            continue
        delay_val = dt_notification - cur_time
        print(meeting['theme'], '-', 'yes', meeting['theme'], 'in', delay_val)

        send_notification.send_with_options(
            args=(meeting['user_id'], meeting['theme'], rem_time_dict['msg']),
            delay=delay_val)
'''
