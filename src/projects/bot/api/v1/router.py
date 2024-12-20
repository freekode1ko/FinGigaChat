"""Главный роутер API V1"""
from fastapi import APIRouter

from api.v1.messages.router import router as messages_router


router = APIRouter()

router.include_router(messages_router, prefix='/messages')
