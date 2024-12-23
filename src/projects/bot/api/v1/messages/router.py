"""API для работы отправки сообщений"""
import datetime

import sqlalchemy as sa
from fastapi import APIRouter, BackgroundTasks

from api.v1.messages import schemas
from db import models
from db.database import async_session
from utils.bot import bot


router = APIRouter(tags=['messages'])


async def send_message_to_users(user_msg):
    """Отправка сообщения пользователю"""
    try:
        if not user_msg.user_roles:
            role_ids = [1]
        else:
            role_ids = user_msg.user_roles

        async with async_session() as session:
            broadcast = models.Broadcast(
                    text=user_msg.message_text,
                    message_type_id=user_msg.message_type_id,
                    function_name=user_msg.function_name,
                    created_at=datetime.datetime.now(),
            )
            session.add(broadcast)
            await session.flush()
            user_ids = await session.execute(
                sa.select(models.RegisteredUser.user_id)
                .filter(models.RegisteredUser.role_id.in_(role_ids)))
            user_ids = user_ids.scalars().all()
            for user_id in user_ids:
                user_mes = await bot.send_message(
                    chat_id=user_id,
                    text=user_msg.message_text,
                    parse_mode=user_msg.parse_mode,
                )
                session.add(
                    models.TelegramMessage(
                        telegram_message_id=user_mes.message_id,
                        user_id=user_id,
                        broadcast_id=broadcast.id,
                        send_datetime=datetime.datetime.now()
                    ))
            await session.commit()

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {'error': str(e), 'full': str(traceback.format_exc())}


@router.post('/send')
async def send_message(user_msg: schemas.BaseMessage, background_tasks: BackgroundTasks):  # TODO: remove
    """Отправить сообщение"""
    background_tasks.add_task(send_message_to_users, user_msg)
    return {'status': 'OK'}
