from fastapi import APIRouter

from api.v1.news.router import router as news_router
from api.v1.quotation.router import router as quotation_router
from api.v1.analytics.router import router as analytics_router
from api.v1.subscriptions.router import router as subscriptions_router
from api.v1.meetings.router import router as meetings_router
from api.v1.auth.router import router as auth_router
from api.v1.products.router import router as products_router
from api.v1.settings.router import router as settings_router

router = APIRouter()

router.include_router(auth_router, prefix='/auth')
router.include_router(products_router, prefix='/products')
router.include_router(settings_router, prefix='/settings')
router.include_router(news_router, prefix='/news')
router.include_router(quotation_router, prefix='/quotation')
router.include_router(analytics_router, prefix='/analytics')
router.include_router(subscriptions_router, prefix='/subscriptions')
router.include_router(meetings_router, prefix='/meetings')
