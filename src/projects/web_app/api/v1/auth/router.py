import re
import random
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi import status

import config

from api.security import set_auth_cookie
from api.v1.common_schemas import Error
from api.dependencies import get_repository, get_current_user
from constants import constants
from constants.texts import texts_manager
from db.repository import UserRepository
from db.redis import redis_client
from db.models import RegisteredUser
from utils.jwt import create_jwt_token
from utils.telegram import validate_telegram_data
from utils.email_send import SmtpSend
from utils.utils import is_valid_email

from api.v1.users.schemas import UserRead
from .schemas import AuthData, AuthConfirmation, TelegramData


router = APIRouter(tags=['auth'])


@router.post(
        "/login",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                'description': 'Некорректная почта или не пройдена авторизация в боте',
                'model': Error,
            },
        }
)
async def login(
    data: AuthData,
    user_repository: Annotated[UserRepository, Depends(get_repository(UserRepository))],
):
    """
    Аутентификация через EMail.
    Подходит для использования приложения вне Telegram.
    """
    if not is_valid_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Введите корпоративную почту'
        )
    if await user_repository.is_new_user_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пожалуйста, сначала зарегистрируйтесь в боте'
        )
    reg_code = str(random.randint(constants.AUTH_CODE_MIN, constants.AUTH_CODE_MAX))
    await redis_client.setex(
        f"reg_code:{data.email}",
        constants.AUTH_CODE_TTL,
        reg_code
    )
    async with SmtpSend(
        config.MAIL_RU_LOGIN,
        config.MAIL_RU_PASSWORD,
        config.MAIL_SMTP_SERVER,
        config.MAIL_SMTP_PORT
    ) as smtp_email:
        message = await texts_manager.get('AUTH_EMAIL_TEXT')
        await smtp_email.send_msg(
            config.MAIL_RU_LOGIN,
            data.email,
            constants.AUTH_MAIL_TITLE,
            message.format(code=reg_code),
        )
    return "ok"


@router.post(
        "/verify",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                'description': 'Неверный одноразовый код',
                'model': Error,
            },
        }
)
async def verify(
    response: Response,
    data: AuthConfirmation,
    user_repository: Annotated[UserRepository, Depends(get_repository(UserRepository))],
):
    """Подтверждение входа с помощью одноразового пароля."""
    reg_code = await redis_client.get(f"reg_code:{data.email}")
    if not reg_code or reg_code != data.reg_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Запросите код еще раз и повторите попытку'
        )
    user_id = await user_repository.get_user_id_by_email(data.email)
    jwt_token = create_jwt_token(user_id, constants.JWT_TOKEN_EXPIRE)
    set_auth_cookie(response, jwt_token)
    await redis_client.delete(f"reg_code:{data.email}")
    return "ok"


@router.post(
        "/validate_telegram",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                'description': 'Невалидные данные Telegram-пользователя',
                'model': Error,
            },
        }
)
async def validate_telegram(data: TelegramData, response: Response):
    """Валидация данных, полученных из Telegram WebApp."""
    if not validate_telegram_data(data):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Некорректные данные пользователя'
        )
    jwt_token = create_jwt_token(user_id=data.id)
    set_auth_cookie(response, jwt_token)
    return "ok"


@router.get(
        "/me",
        response_model=UserRead,
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                'description': 'Ошибка чтения JWT-токена: истек срок действия или неверный токен',
                'model': Error,
            },
            status.HTTP_403_FORBIDDEN: {
                'description': 'Ошибка авторизации: не предоставлен токен или такой пользователь отсутствует',
                'model': Error,
            },
        }
)
async def user_identity(
    current_user: Annotated[RegisteredUser, Depends(get_current_user)],
) -> UserRead:
    """Получение текущего пользователя по JWT-токену."""
    return UserRead.model_validate(current_user)
