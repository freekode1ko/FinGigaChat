"""Вспомогательные функции для отправки, редактирования и удаления сообщений"""
import datetime
from itertools import batched
from typing import Any

import sqlalchemy as sa
from aiogram import types
from aiogram.utils.media_group import MediaGroupBuilder, MediaType
from sqlalchemy.orm import selectinload
import sulguk

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


    @classmethod
    async def edit_message(cls, user_id: int, message_id: int, text: str, parse_mode: str, files: list[Any] | None = None) -> types.Message | bool:
        try:
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
        except Exception as e:
            return


    @staticmethod
    async def delete_message(user_id: int, message_id: int,) -> bool:
        await bot.delete_message(chat_id=user_id, message_id=message_id)

    @staticmethod
    async def _create_media_group_by_files_ids(files: list[Any], caption: str | None = None) -> list[MediaType]:
        media = MediaGroupBuilder(caption=caption)

        for file in files:
            media.add_document(media=types.InputMediaDocument(media=file.telegram_file_id))
        return media.build()

    @staticmethod
    def _transform_text(text: str) -> sulguk.RenderResult:
        return sulguk.transform_html(text)


async def _get_broadcast_by_id(session, broadcast_id) -> models.Broadcast:
    result = await session.execute(
        sa.select(models.Broadcast)
        .options(
            selectinload(models.Broadcast.versions).selectinload(models.BroadcastVersion.telegram_files),
        )
        .filter(models.Broadcast.id == broadcast_id)
    )
    return result.scalar_one()


async def _get_broadcast_version(session, broadcast_id):
    broadcast = await _get_broadcast_by_id(session, broadcast_id)

    broadcast_versions_count = len(broadcast.versions)
    broadcast_latest_version = max(broadcast.versions, key=lambda v: v.created_at) if broadcast.versions else None

    return broadcast, broadcast_versions_count, broadcast_latest_version


async def get_telegram_message(session, user_id: int, broadcast_id: int) -> models.TelegramMessage | None:
    existing_message = await session.execute(
        sa.select(models.TelegramMessage)
        .filter(
            models.TelegramMessage.user_id == user_id,
            models.TelegramMessage.broadcast_id == broadcast_id
        )
    )
    return existing_message.scalar_one_or_none()

async def _extend_users_id_by_field(session, user_ids, field, in_ids):
    stmt = await session.execute(
        sa.select(models.RegisteredUser.user_id)
        .filter(field.in_(in_ids)))
    res = stmt.scalars().all()
    user_ids.extend(res)


async def _get_all_user_ids(
        session,
        user_ids: list[int],
        user_emails: list[str],
        user_roles: list[int]
) -> set[int]:
    if not user_ids:
        user_ids = []

    if user_roles:
        await _extend_users_id_by_field(session, user_ids, models.RegisteredUser.role_id, user_roles)

    if user_emails:
        await _extend_users_id_by_field(session, user_ids, models.RegisteredUser.user_email, user_emails)

    new_user_ids = []
    await _extend_users_id_by_field(session, new_user_ids, models.RegisteredUser.user_id, user_ids)
    return new_user_ids


async def _get_all_users_from_before_broadcast(
        session,
        broadcast_id: int,
        broadcast_latest_version_datetime: datetime.datetime,
) -> list[int]:
    broadcast = await _get_broadcast_by_id(session, broadcast_id)

    if len(broadcast.versions) <= 1:
        return []

    broadcast_before_last_version = min(broadcast.versions, key=lambda x: abs((broadcast_latest_version_datetime - x).seconds))

    stmt = await session.execute(
        sa.select(models.TelegramMessage.user_id)
        .filter(models.TelegramMessage.broadcast_version_id == broadcast_before_last_version.id)
    )
    return stmt.scalars().all() or []


async def _get_broadcast_all_users(session, broadcast_id: int) -> list[int]:
    # При удалении сообщения нужно вернуть все id
    stmt = await session.execute(
        sa.select(models.TelegramMessage.user_id)
        .filter(models.TelegramMessage.broadcast_id == broadcast_id)
    )
    return stmt.scalars().all()


async def _send_or_edit_messages_in_broadcast(
        session,
        user_id: int,
        message_text: str,
        broadcast_id: int,
        broadcast_version_id: int,
        telegram_files: list[int] | None = None,
        existing_message: models.TelegramMessage | None = None
):
    if existing_message:
        message = await MessageManager.edit_message(
            user_id,
            existing_message.telegram_message_id,
            message_text,
            'HTML',
            telegram_files,
        )
        existing_message.broadcast_version_id = broadcast_version_id
        existing_message.send_datetime = datetime.datetime.now()
        existing_message.message_id = message.message_id if message is not None else existing_message.telegram_message_id
        session.add(existing_message)
    else:
        message = await MessageManager.send_message(
            user_id,
            message_text,
            'HTML',
            telegram_files,
        )
        session.add(
            models.TelegramMessage(
                telegram_message_id=message.message_id,
                user_id=user_id,
                broadcast_id=broadcast_id,
                broadcast_version_id=broadcast_version_id,
                send_datetime=datetime.datetime.now()
            ))


async def _get_users_ids(session, broadcast: models.Broadcast, broadcast_latest_version, user_ids, user_emails, user_roles) -> set[int]:
    if not (users_ids := await _get_all_user_ids(session, user_ids, user_emails, user_roles)):
        if broadcast.deleted_at:
            users_ids = await _get_broadcast_all_users(session, broadcast.id)
        else:
            users_ids = await _get_all_users_from_before_broadcast(session, broadcast.id, broadcast_latest_version.created_at)

    return users_ids


async def send_message_to_users(broadcast_id, user_ids: list[int] | None = None, user_emails: list[str]| None = None, user_roles: list[int]| None = None):
    """Отправка сообщения пользователю"""
    try:
        async with async_session() as session:
            broadcast, broadcast_versions_count, broadcast_latest_version = await _get_broadcast_version(session, broadcast_id)

            users_ids = await _get_users_ids(session, broadcast, broadcast_latest_version, user_ids, user_emails, user_roles)

            for users_id_batch in batched(users_ids, config.MAX_MESSAGES_PER_SECOND):
                # TODO: Если удалилась рассылка, то не продолжать отправку
                # _, new_count, _ = await _get_broadcast_version(session, broadcast_id)
                # if new_count != broadcast_versions_count:
                #     make_action_with_message = False

                for user_id in users_id_batch:
                    existing_message = await get_telegram_message(session, user_id, broadcast_id)

                    if existing_message and broadcast.deleted_at is not None:
                        await MessageManager.delete_message(user_id, existing_message.telegram_message_id)
                        continue
                    # send_or_edit_message
                    await _send_or_edit_messages_in_broadcast(
                        session,
                        user_id,
                        broadcast_latest_version.message_text,
                        broadcast.id,
                        broadcast_latest_version.id,
                        existing_message=existing_message,
                    )
            await session.commit()

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {'error': str(e), 'full': str(traceback.format_exc())}
