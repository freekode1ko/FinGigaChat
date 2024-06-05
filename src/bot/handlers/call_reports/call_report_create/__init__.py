"""Хендлеры для создания кол репортов"""

from aiogram import Router

from .handler import router as call_report_insert_router

router = Router()

router.include_routers(
    call_report_insert_router
)
