import re
import random

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, HTTPException, Response, Depends
from fastapi import status

import config

from api.security import get_token, set_auth_cookie
from api.v1.common_schemas import Error
from constants import constants
from constants.texts import texts_manager
from db.database import get_async_session
from db.user import is_new_user_email, get_user_id_by_email, get_user_by_id
from db.redis import redis_client
from utils.jwt import create_jwt_token, read_jwt_token
from utils.telegram import validate_telegram_data
from utils.email_send import SmtpSend

from .schemas import AuthData, AuthConfirmation, TelegramData, UserData


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
async def login(data: AuthData, session: AsyncSession = Depends(get_async_session)):
    """
    Аутентификация через EMail.
    Подходит для использования приложения вне Telegram.
    """
    if not re.search(r'\w+@sber(bank)?.ru', data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Введите корпоративную почту'
        )
    if await is_new_user_email(session, data.email):
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
    data: AuthConfirmation,
    response: Response,
    session: AsyncSession = Depends(get_async_session),
):
    """Подтверждение входа с помощью одноразового пароля."""
    reg_code = await redis_client.get(f"reg_code:{data.email}")
    if not reg_code or reg_code != data.reg_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Запросите код еще раз и повторите попытку'
        )
    user_id = await get_user_id_by_email(session, data.email)
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
        response_model=UserData,
        responses={
            status.HTTP_401_UNAUTHORIZED: {
                'description': 'Ошибка чтения JWT-токена: истек срок действия или неверный токен',
                'model': Error,
            },
        }
)
async def user_identity(
    token: str = Depends(get_token),
    session: AsyncSession = Depends(get_async_session)
):
    """Получение текущего пользователя по JWT-токену."""
    try:
        user_id = read_jwt_token(token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    user = await get_user_by_id(session, user_id)
    return UserData.model_validate(user)
