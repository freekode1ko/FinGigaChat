"""Хендлеры меню кол репортов"""

from aiogram import Router

from .handler import router as call_report_all_view_router

router = Router()

router.include_routers(
    call_report_all_view_router,
)
