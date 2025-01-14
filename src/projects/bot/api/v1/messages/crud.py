from datetime import datetime

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from api.v1.messages import schemas
from api.v1.messages.schemas import FullBroadcast, BroadcastWithVersions, BaseBroadcast
from db import models
from db.database import async_session
from utils.api.pagination import PaginationData


def get_broadcast_schema(broadcast: models.Broadcast, full: bool = False):
    """Broadcast schema"""

    def _create_broadcast(broadcast_version, is_base_broadcast: bool = False):
        broadcast_tmp = BaseBroadcast(
            message_text=broadcast_version.message_text if broadcast_version.message_text else '',
            message_files=[str(file.id) for file in broadcast_version.telegram_files] if broadcast_version.telegram_files else [],
            message_type_id=broadcast_version.message_type_id if broadcast_version else 1,
            user_roles=[str(role.id) for role in broadcast_version.user_roles] if broadcast_version.user_roles else [1],
            create_at=broadcast.created_at if is_base_broadcast else broadcast_version.created_at,
            parse_mode='HTML',
            function_name=broadcast_version.function_name if broadcast_version.function_name else '',
        )
        return FullBroadcast(**broadcast_tmp.model_dump(),
                             deleted_at=broadcast.deleted_at, broadcast_id=broadcast.id) if is_base_broadcast else broadcast_tmp

    latest_version = max(broadcast.versions, key=lambda v: v.created_at) if broadcast.versions else None
    return_broadcast = _create_broadcast(latest_version, is_base_broadcast=True)

    if full:
        versions = [_create_broadcast(version) for version in broadcast.versions]
        return_broadcast = BroadcastWithVersions(**return_broadcast.model_dump(), versions=versions)

    return return_broadcast


async def add_versions_to_broadcast(session, broadcast_id, message):
    new_version = models.BroadcastVersion(
        broadcast_id=broadcast_id,
        message_text=message.message_text,
        message_type_id=message.message_type_id,
        function_name=message.function_name,
        created_at=datetime.now(),
    )
    session.add(new_version)
    await session.flush()

    if message.message_files:
        files = await session.execute(
            sa.select(models.TelegramFile)
            .where(models.TelegramFile.id.in_(message.message_files))
            .options(
                selectinload(models.TelegramFile.broadcast_versions)
            )
        )
        for file in files.scalars().all():
            file.broadcast_versions.append(file)

    if message.user_roles:
        roles = await session.execute(
            sa.select(models.UserRole)
            .where(models.UserRole.id.in_(message.user_roles))
            .options(selectinload(models.UserRole.broadcast_versions))
        )
        for role in roles.scalars().all():
            role.broadcast_versions.append(new_version)


async def get_messages(pagination: PaginationData, full: bool = False):
    """"""
    async with async_session() as session:
        result = await session.execute(
            sa.select(models.Broadcast)
            .options(
                selectinload(models.Broadcast.versions)
                .selectinload(models.BroadcastVersion.telegram_files),

                selectinload(models.Broadcast.versions)
                .selectinload(models.BroadcastVersion.user_roles),
            )
            .limit(pagination.get_db_limit())
            .offset(pagination.get_db_offset())
        )
        broadcasts = result.scalars().all()
        if not broadcasts:
            raise HTTPException(status_code=202, detail="No broadcasts found")

    return [get_broadcast_schema(broadcast, full=full) for broadcast in broadcasts]


async def get_message(broadcast_id: int | None = None, full: bool = False):
    """"""
    async with async_session() as session:
        result = await session.execute(
            sa.select(models.Broadcast)
            .options(
                selectinload(models.Broadcast.versions)
                .selectinload(models.BroadcastVersion.telegram_files),
                selectinload(models.Broadcast.versions)
                .selectinload(models.BroadcastVersion.user_roles)
            )
            .filter(models.Broadcast.id == broadcast_id)
        )
        broadcast = result.scalar_one_or_none()
    if not broadcast:
        raise HTTPException(status_code=404, detail="Broadcast not found")
    return get_broadcast_schema(broadcast, full=full)


async def create_message(message: schemas.CreateBroadcast):
    """"""
    async with async_session() as session:
        new_broadcast = models.Broadcast(created_at=datetime.now())
        session.add(new_broadcast)
        await session.flush()

        await add_versions_to_broadcast(session, broadcast_id=new_broadcast.id, message=message)
        await session.commit()


    return await get_message(new_broadcast.id), new_broadcast.id


#
async def edit_message(message: schemas.CreateBroadcast, broadcast_id: int):
    """"""
    async with async_session() as session:
        result = await session.execute(
            sa.select(models.Broadcast)
            .options(
                selectinload(models.Broadcast.versions).selectinload(models.BroadcastVersion.telegram_files)
            )
            .filter(models.Broadcast.id == broadcast_id)
        )
        broadcast = result.scalar_one_or_none()

        if not broadcast:
            raise HTTPException(status_code=404, detail="Broadcast not found")
        await session.commit()
        await add_versions_to_broadcast(session, broadcast_id=broadcast_id, message=message)
        await session.commit()

    return await get_message(broadcast_id, full=True)


async def delete_message(broadcast_id: int):
    """"""
    async with async_session() as session:
        broadcast = await session.get(models.Broadcast, broadcast_id)
        if broadcast is None:
            raise HTTPException(status_code=404, detail="Broadcast not found")

        broadcast.deleted_at = datetime.now()

        session.add(broadcast)
        await session.commit()
        await session.refresh(broadcast)
        print(broadcast)
