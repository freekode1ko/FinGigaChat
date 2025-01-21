"""API для работы отправки сообщений"""
from typing import Annotated

from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from fastapi import (
    Depends
)

from utils.api.pagination import PaginationData, get_pagination_dep
from utils.messages import send_message_to_users
from . import crud as messages_crud
from .schemas import CreateBroadcast

router = APIRouter(tags=["messages"])


@router.get('/')
async def get_messages(
        pagination: Annotated[
            PaginationData,
            Depends(get_pagination_dep),
        ],
        full: Annotated[bool, Query(description="Номер страницы")] = False
):
    """Получить пользовательское сообщение"""
    print(pagination)
    messages = await messages_crud.get_messages(pagination, full=full)
    return {
        "messages": messages,
        "pagination": pagination
    }


@router.get('/{message_id}')
async def get_message(
        message_id: int,
        full: Annotated[bool, Query(description="Номер страницы")] = False
):
    """Получить пользовательское сообщение"""
    messages = await messages_crud.get_message(message_id, full=full)
    return {
        "message": messages,
    }


@router.post('/')
async def create_message(
        user_msg: CreateBroadcast,
        background_tasks: BackgroundTasks
):
    try:
        message, broadcast_id = await messages_crud.create_message(user_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    background_tasks.add_task(send_message_to_users, broadcast_id, user_msg.users_ids, user_msg.users_emails, user_msg.user_roles)
    return {**message.model_dump()}


@router.patch('/{message_id}')
async def edit_message(
        message_id: int,
        user_msg: CreateBroadcast,
        background_tasks: BackgroundTasks
):
    try:
        message = await messages_crud.edit_message(user_msg, message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    background_tasks.add_task(send_message_to_users, message_id, user_msg.users_ids, user_msg.users_emails, user_msg.user_roles)
    return {**message.model_dump()}


@router.delete('/{message_id}')
async def delete_messages(
        message_id: int,
        background_tasks: BackgroundTasks
):
    await messages_crud.delete_message(message_id)
    background_tasks.add_task(send_message_to_users, message_id)
