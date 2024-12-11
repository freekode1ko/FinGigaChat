"""API для работы тестирования"""

from fastapi import APIRouter

router = APIRouter(tags=["testing"])


@router.get("/")
async def get_test():
    """Получить Hello World"""
    return {"message": "Hello World"}
