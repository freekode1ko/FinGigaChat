"""API для работы с ботом"""
import os
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse

from api.dependencies import get_current_admin
from db.models import RegisteredUser
from .schemas import MessageCreate


router = APIRouter(tags=['bot'])


@router.post(
    '/messages',
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    message: MessageCreate,
    user: RegisteredUser = Depends(get_current_admin),
):
    """
    *Только для администраторов*\n
    Отправить сообщение всем пользователям Telegram-бота.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"http://bot_container:{os.getenv('PORT_BOT')}/api/v1/messages/", json={
            "author_id": user.user_id,
            "message_text": message.message,
            "users_emails": message.user_emails,
        })
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.response.json())
        return response.json()


@router.get('/messages', dependencies=[Depends(get_current_admin)])
async def get_messages(
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Размер страницы")] = 10
):
    """
    *Только для администраторов*\n
    Получить список всех рассылок.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://bot_container:{os.getenv('PORT_BOT')}/api/v1/messages?page={page}&size={size}", follow_redirects=True)
        response_data = response.json()
        if 'detail' in response_data:
            return JSONResponse(content={"messages": [], "pagination": {"page": page, "size": size}})
        return response_data


@router.get('/messages/{broadcast_id}', dependencies=[Depends(get_current_admin)])
async def get_full_message(broadcast_id: int):
    """
    *Только для администраторов*\n
    Получить полную информацию о рассылке.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://bot_container:{os.getenv('PORT_BOT')}/api/v1/messages/{broadcast_id}?full=true")
        response_data = response.json()
        if 'detail' in response_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=response_data.get('detail', 'Error'))
        return response_data


@router.delete('/messages/{broadcast_id}', dependencies=[Depends(get_current_admin)])
async def delete_message(broadcast_id: int):
    """
    *Только для администраторов*\n
    Удалить рассылку.
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"http://bot_container:{os.getenv('PORT_BOT')}/api/v1/messages/{broadcast_id}")
        return response.json()


@router.patch('/messages/{broadcast_id}')
async def update_message(broadcast_id: int, message: MessageCreate, user: RegisteredUser = Depends(get_current_admin)):
    """
    *Только для администраторов*\n
    Обновить рассылку.
    """
    async with httpx.AsyncClient() as client:
        response = await client.patch(f"http://bot_container:{os.getenv('PORT_BOT')}/api/v1/messages/{broadcast_id}", json={
            "author_id": user.user_id,
            "users_emails": message.user_emails,
            "message_text": message.message,
        })
        return response.json()
