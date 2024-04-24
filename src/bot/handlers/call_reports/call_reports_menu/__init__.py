from .handler import router as call_report_all_view_router
#
#
# from .call_reports import router

from aiogram import Router

router = Router()

router.include_routers(
    call_report_all_view_router,
)

