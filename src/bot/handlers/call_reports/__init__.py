from aiogram import Router

from .call_report_create import router as call_report_insert_router
from .call_report_view import router as call_report_view_router
from .call_reports import router as main_router
from .call_reports_menu import router as call_report_all_view_router

router = Router()

router.include_routers(
    main_router,
    call_report_insert_router,
    call_report_all_view_router,
    call_report_view_router,
)
