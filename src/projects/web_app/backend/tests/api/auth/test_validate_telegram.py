"""Тесты для валидации данных из Telegram WebApp"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from constants.constants import JWT_TOKEN_NAME
from tests.constants import MOCK_USER_ID, MOCK_JWT_TOKEN


@pytest.mark.asyncio
async def test_validate_success(_async_client: AsyncClient):
    """
    Проверяем успешный случай валидации данных пользователя Telegram:
        1. Пользователь действительно зашел через Telegram (WebApp)
        2. Пользователю устанавливается JWT-токен в cookies
    """
    with (
        patch('api.v1.auth.router.validate_telegram_data', return_value=True),
        patch('api.v1.auth.router.create_jwt_token', return_value=MOCK_JWT_TOKEN),
    ):
        response = await _async_client.post(
            '/api/v1/auth/validate_telegram',
            json={'id': MOCK_USER_ID, 'data': 'real_tg'},
        )
        assert response.status_code == 200
        assert response.text == '"ok"'
        assert f'{JWT_TOKEN_NAME}={MOCK_JWT_TOKEN}' in response.headers.get('Set-Cookie'), 'Отсутствует cookie с JWT-токеном'


@pytest.mark.asyncio
async def test_verify_invalid_code(_async_client: AsyncClient):
    """
    Проверяем, что попытка валидации некорректных данных приводит к ошибке.
    """
    with patch('api.v1.auth.router.validate_telegram_data', return_value=False):
        response = await _async_client.post(
            '/api/v1/auth/validate_telegram',
            json={'id': MOCK_USER_ID, 'data': 'fake_tg'},
        )
        assert response.status_code == 400
        assert response.json() == {'detail': 'Некорректные данные пользователя'}
