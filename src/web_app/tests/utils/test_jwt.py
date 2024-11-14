"""Тесты модуля для работы с JWT"""

from datetime import datetime, timedelta, timezone
import base64
import time

import jwt
import pytest

from utils.jwt import create_jwt_token, read_jwt_token
from config import JWT_SECRET
from constants.constants import JWT_ALGORITHM


def test_create_jwt_token():
    """
    Проверяем, что payload созданного токена соответствует ожидаемому.
    """
    issued_time = datetime.now(timezone.utc)
    expires_at = issued_time + timedelta(seconds=100)
    encoded_token = create_jwt_token(user_id=1, expires_in=100)
    decoded_token = jwt.decode(encoded_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    assert decoded_token['sub'] == 1, 'Владелец токена (sub) некорректен'
    assert 'iat' in decoded_token, 'Payload должен содержать время создания (iat)'
    assert 'exp' in decoded_token, 'Payload должен содержать время истечения (exp)'
    assert decoded_token['iat'] - issued_time.timestamp(), 'Время создания (iat) некорректно'
    assert decoded_token['exp'] - expires_at.timestamp(), 'Время истечения (exp) некорректно'


def test_read_jwt_token():
    """
    Проверяем, что user_id из токена соответствует ожидаемому.
    """
    issued_time = datetime.now(timezone.utc)
    to_encode = {
        'sub': 1,
        'iat': issued_time,
        'exp': issued_time + timedelta(seconds=100),
    }
    encoded_token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    user_id = read_jwt_token(encoded_token)
    assert user_id == 1, 'Получили некорректный user_id из токена'


def test_read_expired_jwt_token():
    """
    Проверяем, что чтение истекшего токена вызывает ошибку.
    """
    encoded_token = create_jwt_token(user_id=1, expires_in=1)
    time.sleep(2)
    with pytest.raises(ValueError, match='Некорректный токен'):
        read_jwt_token(encoded_token)


def test_read_malformed_jwt_token():
    """
    Проверяем, что чтение поддельного токена вызывает ошибку.
    """
    encoded_token = create_jwt_token(user_id=1, expires_in=100)

    # Подделываем JWT токен так, как это делал бы злоумышленник, который не знает ключ
    header, payload, signature = encoded_token.split('.')
    decoded_payload = base64.urlsafe_b64decode(payload + '==').decode('utf-8')
    malformed_payload = decoded_payload.replace('"sub":1', '"sub":2')
    malformed_payload_encoded = base64.urlsafe_b64encode(malformed_payload.encode('utf-8')).decode('utf-8').rstrip('=')
    malformed_token = f"{header}.{malformed_payload_encoded}.{signature}"

    with pytest.raises(ValueError, match='Некорректный токен'):
        read_jwt_token(malformed_token)
