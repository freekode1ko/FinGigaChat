"""API для работы с белым списком"""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Query, status

from api.v1.whitelist.schemas import WhitelistRead, WhitelistCreate, whitelist_adapter
from api.dependencies import get_current_admin, get_repository
from api.v1.common_schemas import PaginationParams, PaginatedResponse
from db.models import Whitelist
from db.mapper import pydantic_to_sqlalchemy
from db.repository import WhitelistRepository
from utils.utils import is_valid_email


router = APIRouter(tags=['whitelist'])


@router.get(
        '/',
        dependencies=[Depends(get_current_admin)],
)
async def get_whitelist(
    whitelist_repository: Annotated[WhitelistRepository, Depends(get_repository(WhitelistRepository))],
    pagination: Annotated[PaginationParams, Depends()],
    email: str | None = Query(None, min_length=1, max_length=100),
) -> PaginatedResponse[WhitelistRead]:
    """
    *Только для администраторов*\n
    Список E-Mail в белом списке. Поддерживает фильтрацию по email.
    """
    db_emails, total = await whitelist_repository.get_list_with_count(email, pagination.to_db())
    validated_emails = whitelist_adapter.validate_python(db_emails)
    return PaginatedResponse.create(validated_emails, total, pagination.size)


@router.post(
        '/',
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(get_current_admin)],
)
async def add_to_whitelist(
    whitelist_repository: Annotated[WhitelistRepository, Depends(get_repository(WhitelistRepository))],
    data: WhitelistCreate,
):
    """
    *Только для администраторов*\n
    Добавить E-Mail в белый список.
    """
    if not is_valid_email(data.user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Введите корпоративную почту'
        )
    if await whitelist_repository.get_by_pk(data.user_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Такой адрес уже есть в базе',
        )
    await whitelist_repository.create(pydantic_to_sqlalchemy(data, Whitelist))


@router.delete(
        '/{email}',
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(get_current_admin)],
)
async def remove_from_whitelist(
    whitelist_repository: Annotated[WhitelistRepository, Depends(get_repository(WhitelistRepository))],
    email: str,
):
    """
    *Только для администраторов*\n
    Удалить E-Mail из белого списка.
    """
    if (email_db := await whitelist_repository.get_by_pk(email)) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Проверьте корректность введенного адреса',
        )
    await whitelist_repository.delete(email_db)
