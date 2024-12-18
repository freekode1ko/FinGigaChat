"""API для работы с ботом"""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.v1.common_schemas import PaginationParams, PaginatedResponse
from api.dependencies import get_current_admin
from .schemas import BotInfoRead, MessageCreate, MessageRead


router = APIRouter(tags=['bot'])


@router.get(
    '/',
    response_model=BotInfoRead,
    dependencies=[Depends(get_current_admin)],
)
async def get_bot_info():
    """
    *Только для администраторов*\n
    Получить текущую информацию о боте (имя, описание).
    """
    return BotInfoRead(name='Test', bio='Test')


@router.get(
    '/messages',
    response_model=PaginatedResponse[MessageRead],
    dependencies=[Depends(get_current_admin)],
)
async def get_messages(
    pagination: Annotated[PaginationParams, Depends()],
    message_type_id: int | None = Query(None),
):
    """
    *Только для администраторов*\n
    Получить список сообщений бота.
    """
    ...


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
    ...


@router.put(
    '/messages/{message_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
async def update_message(message_id: int, message: MessageCreate):
    """
    *Только для администраторов*\n
    Обновить отправленное сообщение.
    """
    ...


@router.delete(
    '/messages/{message_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_admin)],
)
async def delete_message(message_id: int):
    """
    *Только для администраторов*\n
    Удалить отправленное сообщение у всех пользователей.
    """
    ...
