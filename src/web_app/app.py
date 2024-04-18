from contextlib import asynccontextmanager
import ssl

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

import config
from db.meeting import get_user_meetings, add_meeting, get_user_email
import utils


@asynccontextmanager
async def lifespan(app: FastAPI):
    utils.add_notify_job()
    utils.scheduler.start()
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")


if not config.DEBUG:
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(config.STATIC_CHAIN_PATH, keyfile=config.STATIC_KEY_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/meeting/show", response_class=HTMLResponse)
async def show_meetings(request: Request, ):
    return templates.TemplateResponse("meeting.html", {"request": request})


@app.get("/meeting/show/{user_id}", response_class=JSONResponse)
async def show_user_meetings(user_id: int | str):
    meetings = get_user_meetings(user_id)
    meetings = utils.format_date(meetings)
    return JSONResponse(meetings)


@app.get('/meeting/create')
async def create_meeting_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.get('/meeting/save')
async def create_meeting(user_id, theme, date_start, date_end, description, timezone):
    data = {
        'user_id': user_id,
        'theme': theme,
        'date_start': date_start,
        'date_end': date_end,
        'description': description,
        'timezone': timezone
    }
    data = utils.reformat_data(data)
    add_meeting(data)
    utils.add_notify_job(meeting=data)

    user_email = get_user_email(user_id=user_id)
    with (utils.SmtpSend(config.MAIL_RU_LOGIN, config.MAIL_RU_PASSWORD, config.MAIL_SMTP_SERVER, config.MAIL_SMTP_PORT)
          as smtp_email):
        smtp_email.send_meeting(user_email, data)

    return 'OK'
