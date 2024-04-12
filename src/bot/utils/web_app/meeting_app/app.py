import os

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from db.web_app.meeting import *
from module.email_send import SmtpSend
from utils.web_app.meeting_app.utils import format_date, reformat_data
from configs.config import mail_smpt_port, mail_smpt_server
# from schedular import send_schedular_new_data

app = FastAPI()

origins = [
    "http://localhost:63342",
    "https://alinlpkv.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    smtp = SmtpSend(os.getenv('MAIL_RU_LOGIN'), os.getenv('MAIL_RU_PASSWORD'), mail_smpt_server, mail_smpt_port)
    with smtp:
        smtp.send_meeting(user_email, data)

    return 'OK'
