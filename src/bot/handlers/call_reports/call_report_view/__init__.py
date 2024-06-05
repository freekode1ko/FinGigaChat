"""Хендлеры для просмотра кол репортов"""

from aiogram import Router

from .handler import router as call_report_view

router = Router()

router.include_routers(
    call_report_view,
)
