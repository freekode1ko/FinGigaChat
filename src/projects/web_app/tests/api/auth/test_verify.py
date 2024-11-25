"""Тесты для верификации одноразового кода"""

from unittest.mock import patch

import pytest
from httpx import AsyncClient

from constants.constants import JWT_TOKEN_NAME
from tests.constants import MOCK_REG_CODE, MOCK_USER_ID, MOCK_JWT_TOKEN


@pytest.mark.asyncio
async def test_verify_success(_async_client: AsyncClient, mock_redis_client):
    """
    Проверяем успешный случай верификации одноразового кода:
        1. Код для данного пользователя найден в Redis
        2. Пользователю устанавливается JWT-токен в cookies
        3. Код для данного пользователя удален из Redis
    """
    email = 'test@sberbank.ru'
    with (
        patch('api.v1.auth.router.redis_client', mock_redis_client),
        patch('api.v1.auth.router.get_user_id_by_email', return_value=MOCK_USER_ID),
        patch('api.v1.auth.router.create_jwt_token', return_value=MOCK_JWT_TOKEN),
    ):
        response = await _async_client.post(
            '/api/v1/auth/verify',
            json={'email': email, 'reg_code': MOCK_REG_CODE},
        )
        assert response.status_code == 200
        assert response.text == '"ok"'
        assert f'{JWT_TOKEN_NAME}={MOCK_JWT_TOKEN}' in response.headers.get('Set-Cookie'), 'Отсутствует cookie с JWT-токеном'
        mock_redis_client.delete.assert_called_once_with(f'reg_code:{email}')


@pytest.mark.asyncio
async def test_verify_invalid_code(_async_client: AsyncClient, mock_redis_client):
    """
    Проверяем, что верификация некорректного кода невозможна.
    """
    email = 'test@sberbank.ru'
    with patch('api.v1.auth.router.redis_client', mock_redis_client):
        response = await _async_client.post(
            '/api/v1/auth/verify',
            json={'email': email, 'reg_code': 'invalid'},
        )
        assert response.status_code == 400
        assert response.json() == {'detail': 'Запросите код еще раз и повторите попытку'}


@pytest.mark.asyncio
async def test_verify_code_not_found(_async_client: AsyncClient, mock_redis_client):
    """
    Проверяем, что верификация истекшего (удаленного) кода невозможна.
    """
    email = 'test@sberbank.ru'
    with patch("api.v1.auth.router.redis_client", mock_redis_client):
        mock_redis_client.get.return_value = None
        response = await _async_client.post(
            '/api/v1/auth/verify',
            json={'email': email, 'reg_code': MOCK_REG_CODE}
        )
        assert response.status_code == 400
        assert response.json() == {'detail': 'Запросите код еще раз и повторите попытку'}
