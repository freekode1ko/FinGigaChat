"""Аутентификация в сервисе мониторинга"""
import requests

from configs.config import MONITORING_LOGIN_URL, MONITORING_USER_PASSWORD, MONITORING_USER_LOGIN
from log.logger_base import logger


class AuthorizationError(Exception):
    """Ошибка аутентификации"""


def get_access_token() -> str:
    """Получение токена доступа к мониторингу."""
    logger.info('Получение токена доступа')
    try:
        r = requests.post(
            url=MONITORING_LOGIN_URL,
            data={'username': MONITORING_USER_LOGIN, 'password': MONITORING_USER_PASSWORD}
        )
        if r.status_code == 200:
            logger.info(f'Токен для пользователя {MONITORING_USER_LOGIN} получен')
            return r.json()['access_token']
        raise AuthorizationError(f'Проблемы с получением токена, ответ: {r.status_code} {r.text}')
    except Exception as e:
        logger.error(f'Ошибка при получении токена {e}')
        raise
