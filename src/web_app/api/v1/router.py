from fastapi import APIRouter

from api.v1.news.news import router as news_router
from api.v1.quotation.quotation import router as quotation_router
from api.v1.analytics.analytics import router as analytics_router
from api.v1.subscriptions.subscriptions import router as subscriptions_router
from api.v1.meetings.meetings import router as meetings_router

router = APIRouter()

router.include_router(news_router, prefix='/news')
router.include_router(quotation_router, prefix='/quotation')
router.include_router(analytics_router, prefix='/analytics')
router.include_router(subscriptions_router, prefix='/subscriptions')
router.include_router(meetings_router, prefix='/meetings')
