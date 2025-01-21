from datetime import datetime

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.v1.messages import schemas
from api.v1.messages.schemas import FullBroadcast, BroadcastWithVersions, BaseBroadcast
from db import models
from db.database import async_session
from utils.api.pagination import PaginationData


def get_broadcast_schema(
        broadcast: models.Broadcast,
        full: bool = False
) -> BaseBroadcast | FullBroadcast | BroadcastWithVersions:
    """Создание разных схем Broadcast в зависимости от запроса"""

    def _create_broadcast(
            broadcast_version: models.BroadcastVersion,
            is_base_broadcast: bool = False
    ) -> BaseBroadcast | FullBroadcast:
        """Создание схемы Broadcast"""
        broadcast_tmp = BaseBroadcast(
            author_id=broadcast_version.author_id,
            message_text=broadcast_version.message_text if broadcast_version.message_text else '',
            message_files=[str(file.id) for file in broadcast_version.telegram_files] if broadcast_version.telegram_files else [],
            message_type_id=broadcast_version.message_type_id if broadcast_version else 1,
            create_at=broadcast.created_at if is_base_broadcast else broadcast_version.created_at,
            parse_mode='HTML',
            function_name=broadcast_version.function_name if broadcast_version.function_name else '',
        )
        return FullBroadcast(**broadcast_tmp.model_dump(),
                             deleted_at=broadcast.deleted_at, broadcast_id=broadcast.id) if is_base_broadcast else broadcast_tmp

    latest_version: models.BroadcastVersion = max(broadcast.versions, key=lambda v: v.created_at) if broadcast.versions else None
    return_broadcast = _create_broadcast(latest_version, is_base_broadcast=True)

    return BroadcastWithVersions(
        **return_broadcast.model_dump(),
        versions=[_create_broadcast(version) for version in broadcast.versions]
    ) if full else return_broadcast


async def add_versions_to_broadcast(
        session: AsyncSession,
        broadcast_id: int,
        message: schemas.CreateBroadcast
):
    new_version = models.BroadcastVersion(
        author_id=message.author_id,
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
