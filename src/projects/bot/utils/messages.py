"""Вспомогательные функции для отправки, редактирования и удаления сообщений"""
import datetime
from itertools import batched
from typing import Any

import sqlalchemy as sa
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder, MediaType
from sqlalchemy.orm import selectinload
from sulguk import transform_html, RenderResult

from configs import config
from db import models
from db.database import async_session
from utils.bot import bot


class MessageManager:

    @classmethod
    async def send_message(cls, user_id: int, text: str, parse_mode: str, files: list[Any] | None = None) -> types.Message:
        result = cls._transform_text(text)
        if files:
            return await bot.send_media_group(
                chat_id=user_id,
                parse_mode=parse_mode,
                media=cls._create_media_group_by_files_ids(files, caption=result.text),
            )
        return await bot.send_message(
            chat_id=user_id,
            text=result.text,
            parse_mode=parse_mode,
            entities=result.entities,
        )


    @staticmethod
    async def edit_message(cls, user_id: int, message_id: int, text: str, parse_mode: str, files: list[Any] | None = None) -> types.Message | bool:
        result = cls._transform_text(text)
        if files:
            await bot.edit_message_caption(
                message_id=message_id,
                chat_id=user_id,
                caption=result.text,
                parse_mode=parse_mode,
                entities=result.entities
            )
            return await bot.edit_message_media(
                message_id=message_id,
                chat_id=user_id,
                media=cls._create_media_group_by_files_ids(files, caption=result.text),
            )

        return await bot.edit_message_text(
            chat_id=user_id,
            message_id=message_id,
            text=result.text,
            parse_mode=parse_mode,
            entities=result.entities,
        )

    @staticmethod
    async def delete_message(cls, user_id: int, message_id: int,) -> bool:
        await bot.delete_message(chat_id=user_id, message_id=message_id)

    @staticmethod
    async def _create_media_group_by_files_ids(files: list[Any], caption: str | None = None) -> list[MediaType]:
        media = MediaGroupBuilder(caption=caption)

        for file in files:
            media.add_document(media=types.InputMediaDocument(media=file.telegram_file_id))
        return media.build()

    @staticmethod
    def _transform_text(text: str) -> RenderResult:
        return transform_html(text)


async def send_message_to_users(broadcast_id):
    """Отправка сообщения пользователю"""

    async def _get_broadcast_version(session, broadcast_id):
        result = await session.execute(
            sa.select(models.Broadcast)
            .options(
                selectinload(models.Broadcast.versions).selectinload(models.BroadcastVersion.telegram_files),
                selectinload(models.Broadcast.versions).selectinload(models.BroadcastVersion.user_roles),
            )
            .filter(models.Broadcast.id == broadcast_id)
        )
        broadcast = result.scalar_one()
        broadcast_versions_count = len(broadcast.versions)
        broadcast_latest_version = max(broadcast.versions, key=lambda v: v.created_at) if broadcast.versions else None

        return broadcast, broadcast_versions_count, broadcast_latest_version

    try:
        print('start')
        async with async_session() as session:
            broadcast, broadcast_versions_count, broadcast_latest_version = await _get_broadcast_version(session, broadcast_id)

            users_ids = await session.execute(
                sa.select(models.RegisteredUser.user_id)
                .filter(models.RegisteredUser.role_id.in_([role.id for role in broadcast_latest_version.user_roles])))
            users_ids = users_ids.scalars().all()

            for users_id_batch in batched(users_ids, config.MAX_MESSAGES_PER_SECOND):
                _, new_count, _ = await _get_broadcast_version(session, broadcast_id)
                if new_count != broadcast_versions_count:
                    break
                for user_id in users_id_batch:
                    existing_message = await session.execute(
                        sa.select(models.TelegramMessage)
                        .filter(
                            models.TelegramMessage.user_id == user_id,
                            models.TelegramMessage.broadcast_id == broadcast_id
                        )
                    )

                    existing_message = existing_message.scalar_one_or_none()
                    if existing_message:
                        if broadcast.deleted_at is not None:
                            await MessageManager.delete_message(user_id, existing_message.telegram_message_id)
                            return

                        message = await MessageManager.edit_message(
                            user_id,
                            existing_message.telegram_message_id,
                            broadcast_latest_version.message_text,
                            'HTML',
                            broadcast_latest_version.telegram_files,
                        )
                        existing_message.broadcast_version_id = broadcast_latest_version.id
                        existing_message.send_datetime = datetime.datetime.now()
                        existing_message.message_id = message.message_id
                        session.add(existing_message)
                    else:
                        message = await MessageManager.send_message(
                            user_id,
                            broadcast_latest_version.message_text,
                            'HTML',
                            broadcast_latest_version.telegram_files,
                        )
                        session.add(
                            models.TelegramMessage(
                                telegram_message_id=message.message_id,
                                user_id=user_id,
                                broadcast_id=broadcast.id,
                                broadcast_version_id=broadcast_latest_version.id,
                                send_datetime=datetime.datetime.now()
                            ))
            await session.commit()

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {'error': str(e), 'full': str(traceback.format_exc())}
