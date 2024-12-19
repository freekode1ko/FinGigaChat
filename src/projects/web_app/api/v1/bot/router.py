"""API для работы с ботом"""
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_admin
from .schemas import MessageCreate


router = APIRouter(tags=['bot'])


@router.post(
    '/messages',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def send_message(message: MessageCreate):
    """
    *Только для администраторов*\n
    Отправить сообщение всем пользователям Telegram-бота.
    """
    # DEMO
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://bot_container:{os.getenv('PORT_BOT')}/api/v1/message/", json={
            "message": message.message,
        })
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.response.json())
        return response.json()
