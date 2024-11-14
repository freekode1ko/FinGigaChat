import jwt

from config import JWT_SECRET
from constants.constants import JWT_ALGORITHM, JWT_TOKEN_EXPIRE
from datetime import datetime, timedelta, timezone


def create_jwt_token(user_id: int, expires_in: int = JWT_TOKEN_EXPIRE) -> str:
    """
    Создание JWT-токена для пользователя.

    :param int user_id: Идентификатор пользователя
    :param int expires_in: Время жизни токена в секундах
    :return: JWT-токен
    """
    issued_time = datetime.now(timezone.utc)
    to_encode = {
        'sub': user_id,
        'iat': issued_time,
        'exp': issued_time + timedelta(seconds=expires_in),
    }
    jwt_token = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jwt_token


def read_jwt_token(token: str) -> int:
    """
    Декодирование JWT-токена пользователя. Если токен валидный
    возвращает (int) идентификатор пользователя. В противном
    случае вызывает ошибку ValueError (некорректный токен).

    :param str token: JWT-токен
    :return: Идентификатор пользователя
    """
    try:
        result = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise ValueError('Некорректный токен')
    return int(result['sub'])
