"""API для работы с пользователями"""
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, Query, status

from api.dependencies import get_current_admin, get_repository
from api.v1.common_schemas import PaginationParams, PaginatedResponse
from db.models import RegisteredUser
from db.mapper import pydantic_to_sqlalchemy
from db.repository import UserRepository, UserRoleRepository

from .schemas import UserRead, UserUpdate, UserRoleRead, users_adapter


router = APIRouter(tags=['users'])


@router.get(
        '/',
        dependencies=[Depends(get_current_admin)],
)
async def get_users(
    user_repository: Annotated[UserRepository, Depends(get_repository(UserRepository))],
    pagination: Annotated[PaginationParams, Depends()],
    email: str | None = Query(None, min_length=1, max_length=100),
    role_id: int | None = Query(None, gt=0),
) -> PaginatedResponse[UserRead]:
    """
    *Только для администраторов*\n
    Список пользователей. Поддерживает фильтрацию по email и роли.
    """
    db_users, total = await user_repository.get_list_with_count(email, role_id, pagination.to_db())
    validated_users = users_adapter.validate_python(db_users)
    return PaginatedResponse.create(validated_users, total, pagination.size)


@router.patch(
        '/{user_email}',
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(get_current_admin)],
)
async def update_user(
    user_repository: Annotated[UserRepository, Depends(get_repository(UserRepository))],
    user_role_repository: Annotated[UserRoleRepository, Depends(get_repository(UserRoleRepository))],
    user_email: str,
    user_update: UserUpdate,
):
    """
    *Только для администраторов*\n
    Обновление роли пользователя.
    """
    if (user_db := await user_repository.get_user_by_email(user_email)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден',
        )
    if user_update.role_id is not None and await user_role_repository.get_by_pk(user_update.role_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Проверьте корректность ID указанной роли',
        )
    await user_repository.update(pydantic_to_sqlalchemy(user_update, RegisteredUser, user_db))


@router.get(
        '/roles',
        response_model=list[UserRoleRead],
        dependencies=[Depends(get_current_admin)],
)
async def get_user_roles(
    user_role_repository: Annotated[UserRoleRepository, Depends(get_repository(UserRoleRepository))],
):
    """
    *Только для администраторов*\n
    Список ролей пользователей.
    """
    db_roles = await user_role_repository.get_list()
    return db_roles
