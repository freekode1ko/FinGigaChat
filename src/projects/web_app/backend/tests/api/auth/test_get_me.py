"""Тесты для получения текущего пользователя по JWT-токену"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from constants.constants import JWT_TOKEN_NAME
from utils.jwt import create_jwt_token
from db import models
from tests.constants import MOCK_USER_ID


@pytest.mark.asyncio
async def test_get_me_success(
        _async_client: AsyncClient,
        _async_session: AsyncSession,
):
    """
    Проверяем успешный случай получения текущего пользователя:
        1. Пользователь существует в базе данных
        2. Передан корректный JWT-токен, позволяющий идентифицировать пользователя
        3. Пользователю возвращаются его email и id
    """
    user_role = models.UserRole(
        name="test",
        description="test",
    )
    _async_session.add(user_role)
    await _async_session.flush()

    user = models.RegisteredUser(
        user_id=MOCK_USER_ID,
        username='name',
        user_email=(user_email := 'email'),
        full_name='full_name',
        user_type='type',
        user_status='status',
        role_id=user_role.id,
    )
    _async_session.add(user)
    await _async_session.commit()

    token = create_jwt_token(MOCK_USER_ID, expires_in=100)
    response = await _async_client.get(
        '/api/v1/auth/me',
        cookies={JWT_TOKEN_NAME: token}
    )
    assert response.status_code == 200
    assert response.json() == {'id': MOCK_USER_ID, 'email': user_email}


@pytest.mark.asyncio
async def test_get_me_invalid_token(_async_client: AsyncClient):
    """
    Проверяем, что получение текущего пользователя с невалидным токеном невозможно.
    """
    response = await _async_client.get(
        '/api/v1/auth/me',
        cookies={JWT_TOKEN_NAME: 'invalid'}
    )
    assert response.status_code == 401
    assert response.json() == {'detail': 'Некорректный токен'}


@pytest.mark.asyncio
async def test_get_me_no_token(_async_client: AsyncClient):
    """
    Проверяем, что получение текущего пользователя без токена невозможно.
    """
    response = await _async_client.get('/api/v1/auth/me')
    assert response.status_code == 403
