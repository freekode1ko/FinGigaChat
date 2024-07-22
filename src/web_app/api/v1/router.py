from fastapi import APIRouter

from api.v1.news.news import router as news_router
from api.v1.quotation.quotation import router as quotation_router

router = APIRouter()

router.include_router(news_router, prefix='/news')
router.include_router(quotation_router, prefix='/quotation')
