from datetime import datetime

import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from api.v1.messages import schemas
from api.v1.messages.utils import get_broadcast_schema, add_versions_to_broadcast
from db import models
from db.database import async_session
from utils.api.pagination import PaginationData


async def get_messages(pagination: PaginationData, full: bool = False):
    """"""
    async with async_session() as session:
        result = await session.execute(
            sa.select(models.Broadcast)
            .options(
                selectinload(models.Broadcast.versions)
                .selectinload(models.BroadcastVersion.telegram_files),
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
