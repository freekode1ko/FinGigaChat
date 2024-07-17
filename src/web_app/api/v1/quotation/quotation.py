from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from api.v1.quotation.service import *
from api.v1.quotation.schemas import ExchangeSectionData
from utils.templates import templates

router = APIRouter()


@router.get('/popular')
async def popular_quotation(request: Request) -> ExchangeSectionData:
    return ExchangeSectionData(
        sections=(await get_quotation_from_fx()),
    )


@router.get('/dashboard')
async def dashboard_quotation(request: Request) -> ExchangeSectionData:
    return ExchangeSectionData(
        sections=[
            *(await get_quotation_from_fx()),
            await get_quotation_from_eco(),
            await get_quotation_from_bonds(),
            await get_quotation_from_commodity(),
        ]
    )


@router.get("/show", response_class=HTMLResponse)
async def show_quotes(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("quotation.html", {"request": request})


@router.get("/dashboard/show", response_class=HTMLResponse)
async def show_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("dashboard.html", {"request": request})
