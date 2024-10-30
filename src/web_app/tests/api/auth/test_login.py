"""Тесты для аутентификации"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from tests.constants import MOCK_REG_CODE


@pytest.mark.asyncio
async def test_login_success(_async_client: AsyncClient, mock_redis_client, mock_smtp_send):
    """
    Проверяем успешный случай аутентификаци:
        1. Пользователь заходит с корпоративной почты и зарегистрировался в боте
        2. Одноразовый код генерируется и устанавливается в Redis
        3. Пользователю отправляется письмо с кодом
    """
    email = 'test@sberbank.ru'
    with (
        patch('api.v1.auth.router.redis_client', mock_redis_client),
        patch('api.v1.auth.router.is_new_user_email', return_value=False),
        patch('api.v1.auth.router.random.randint', return_value=int(MOCK_REG_CODE)),
        patch('api.v1.auth.router.SmtpSend.send_msg', mock_smtp_send.send_msg)
    ):
        response = await _async_client.post('/api/v1/auth/login', json={'email': email})
        assert response.status_code == 200
        assert response.text == '"ok"'
        assert mock_redis_client.setex.called, 'Код не установлен в Redis'
        assert mock_smtp_send.send_msg.called, 'Код не отправлен на почту'


@pytest.mark.asyncio
async def test_login_invalid_email(_async_client: AsyncClient):
    """
    Проверяем, что аутентификация с некорректной почтой невозможна.
    """
    response = await _async_client.post(
        '/api/v1/auth/login',
        json={'email': 'test@test.com'},
    )
    assert response.status_code == 400
    assert response.json() == {'detail': 'Введите корпоративную почту'}


@pytest.mark.asyncio
async def test_login_not_registered_email(_async_client: AsyncClient):
    """
    Проверяем, что аутентификация с незарегистрированной почтой невозможна.
    """
    with patch('api.v1.auth.router.is_new_user_email', return_value=True):
        response = await _async_client.post(
            '/api/v1/auth/login',
            json={'email': 'test@sberbank.ru'},
        )
        assert response.status_code == 400
        assert response.json() == {'detail': 'Пожалуйста, сначала зарегистрируйтесь в боте'}
