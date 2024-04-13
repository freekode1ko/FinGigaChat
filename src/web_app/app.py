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
# from schedular import send_schedular_new_data

app = FastAPI()
app = FastAPI()
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('/etc/letsencrypt/live/ai-bankir-helper-dev.ru/fullchain.pem', keyfile='/etc/letsencrypt/live/ai-bankir-helper-dev.ru/privkey.pem')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[MEETING_PAGES],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
