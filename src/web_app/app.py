import ssl
from pathlib import Path

from contextlib import asynccontextmanager
import aiohttp
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import config
import utils
from db.meeting import get_user_meetings, add_meeting, get_user_email
from log.logger_base import selector_logger
from api.router import router as api_router
from constants import constants
from utils.decorators import handle_jinja_template_exceptions
from utils.templates import templates


logger = selector_logger(config.LOG_FILE, config.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await utils.add_notify_job(logger)
    utils.scheduler.start()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api")
app.mount(
    '/static',
    StaticFiles(directory=str(constants.PROJECT_DIR / 'frontend' / 'static')),
    name="static"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/meeting/show", response_class=HTMLResponse)
async def show_meetings(request: Request):
    return templates.TemplateResponse("meeting.html", {"request": request})


@app.get("/meeting/show/{user_id}", response_class=JSONResponse, deprecated=True)
async def show_user_meetings(user_id: int | str):
    meetings = await get_user_meetings(user_id)
    meetings = utils.format_date(meetings)
    logger.info('Пользователю %s показано %d встреч', user_id, len(meetings))
    return JSONResponse(meetings)


@app.get('/meeting/create')
async def create_meeting_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.get('/meeting/save', deprecated=True)
async def create_meeting(
        user_id: int | str,
        theme: str,
        date_start: str,
        date_end: str,
        description: str,
        timezone: int
) -> str:
    data = {
        'user_id': user_id,
        'theme': theme,
        'date_start': date_start,
        'date_end': date_end,
        'description': description,
        'timezone': timezone
    }
    data = utils.reformat_data(data)
    meeting_id = await add_meeting(data)
    logger.info('Встреча %s пользователя %s сохранена в бд', theme, user_id)

    data['meeting_id'] = meeting_id
    await utils.add_notify_job(logger=logger, meeting=data)

    user_email = await get_user_email(user_id=user_id)
    with (utils.SmtpSend(config.MAIL_RU_LOGIN, config.MAIL_RU_PASSWORD, config.MAIL_SMTP_SERVER, config.MAIL_SMTP_PORT)
          as smtp_email):
        smtp_email.send_meeting(user_email, data)
    logger.info('Информация о встрече %s пользователя %s отправлена на почту', theme, user_id)

    return 'OK'

@app.get("/{full_path:path}", response_class=HTMLResponse)
@handle_jinja_template_exceptions
async def show_react_app(request: Request, full_path: str) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})
