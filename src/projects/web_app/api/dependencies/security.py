from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie

from api.dependencies import get_repository
from constants import constants
from db.repository import UserRepository
from utils.jwt import read_jwt_token


cookie_scheme = APIKeyCookie(name=constants.JWT_TOKEN_NAME)


def current_user(
    admin: bool = False, 
    optional: bool = False,
):
    """Возвращает текущего пользователя в зависимости от настроек"""
    async def wrapper(
        user_repository: Annotated[UserRepository, Depends(get_repository(UserRepository))],
        token: Annotated[str | None, Depends(cookie_scheme)],
    ):
        if token is None:
            if optional:
                return None
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Авторизуйтесь, чтобы получить доступ",
            )
        try:
            user_id = read_jwt_token(token)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            )
        user = await user_repository.get_by_pk(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )
        if admin and not user.role_id == 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав доступа",
            )
        return user
    return wrapper


get_current_user = current_user()
get_current_admin = current_user(admin=True)
get_optional_user = current_user(optional=True)
