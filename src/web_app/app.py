import ssl

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    await utils.add_notify_job(logger)
    utils.scheduler.start()
    yield

logger = selector_logger(config.LOG_FILE, config.LOG_LEVEL)

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

if True:
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(config.STATIC_CHAIN_PATH, keyfile=config.STATIC_KEY_PATH)

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


@app.get("/meeting/show/{user_id}", response_class=JSONResponse)
async def show_user_meetings(user_id: int | str):
    meetings = await get_user_meetings(user_id)
    meetings = utils.format_date(meetings)
    logger.info('Пользователю %s показано %d встреч', user_id, len(meetings))
    return JSONResponse(meetings)


@app.get('/meeting/create')
async def create_meeting_form(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})


@app.get('/meeting/save')
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


@app.get('/quotation/{currency}')
async def get_quotes(currency: str) -> JSONResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://open.er-api.com/v6/latest/{currency}') as response:
            if response.status != 200:
                raise Exception

            content = await response.json()
            return JSONResponse(content['rates'])


@app.get('/quotation')
async def get_quotation(from_currency: str, to_currency) -> JSONResponse:
    async with (aiohttp.ClientSession() as session):
        async with session.get(
                f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&apikey=NH8NVX5T3WA054E6'
        ) as response:
            if response.status != 200:
                raise Exception

            content = await response.json()
            ret = {
                'from_currency': from_currency,
                'to_currency': to_currency,
                'Time Series FX': content['Time Series FX (Daily)']
            }

            return JSONResponse(ret)


@app.get('/news/')
async def get_news() -> JSONResponse:
    return JSONResponse(
        {
            'news': [
                {
                    'section': 'Валютный рынок и процентные ставки - 3 июля 2024.',
                    'title': 'Укрепление рубля может продолжиться',
                    'text': "Валютный рынок: укрепление рубля может продолжиться. Вчера рубль подешевел до 11,94 за юань, но вечером восстановился до 11,8, поскольку спрос на валюту сейчас невелик. Коммерсант сообщил, что Ozon столкнулся со сложностями при проведении трансграничных платежей. В частности, возникли проблемы с оформлением заказов крупной бытовой техники из Китая.\nСегодня (03 июл, '24) утром рубль подешевел до 11,87 за юань. Однако мы полагаем, что это ослабление временно и спрос на валюту может снизиться, а экспортеры будут ее постепенно продавать для выплаты крупных налогов и дивидендов в июле в размере 2,3 трлн руб. - максимум с октября 2022 года. В этих условиях рубль может укрепиться до 11,7 за юань.",
                    'date': "03 июл, '24",
                },
                {
                    'section': 'Валютный рынок и процентные ставки - 2 июля 2024.',
                    'title': 'Укрепление рубля может возобновиться',
                    'text': "Валютный рынок: укрепление рубля может возобновиться. Вчера рубль продолжил дешеветь после окончания периода налоговых выплат и отступил еще на 1% почти до 11,9 за юань. Обороты торгов по паре CNY/RUB на спотовом рынке МосБиржи снизились на 60 млрд руб. до 172 млрд руб., что говорит об уменьшении активности экспортеров.",
                    'date': "02 июл, '24",
                }
            ]
        }
    )

@app.get("/news/show", response_class=HTMLResponse)
async def show_news(request: Request):
    return templates.TemplateResponse("news.html", {"request": request})


@app.get("/quotes/show", response_class=HTMLResponse)
async def show_quotes(request: Request):
    return templates.TemplateResponse("quotation.html", {"request": request})
