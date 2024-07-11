"""API для работы новостей"""
from datetime import datetime

import sqlalchemy as sa
from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse
from utils.templates import templates

from db.database import async_session

router = APIRouter()


@router.get('/')
async def get_news() -> JSONResponse:
    async with async_session() as session:
        sel = sa.text('select * from article where id in( select article_id from relation_client_article where client_score >3)')
        result = await session.execute(sel)
        result = result.all()
    data = []

    for number, i in enumerate(result):
        if number > 10:
            break
        data.append(
            {
                'section': i[3].strftime("%d.%m.%Y"),
                'title': i[2],
                'text': i[5],
                'date': i[3].strftime("%d.%m.%Y"),
            }
        )

    return JSONResponse(
        {
            'news': data,
        }
    )


@router.get("/show", response_class=HTMLResponse)
async def show_news(request: Request):
    return templates.TemplateResponse("news.html", {"request": request})
