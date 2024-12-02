"""Аутентификация в сервисе мониторинга"""
import requests

from configs.config import MONITORING_LOGIN_URL, MONITORING_USER_LOGIN, MONITORING_USER_PASSWORD
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
    except requests.RequestException as e:
        logger.error(f'Ошибка при получении токена {e}')
        raise

    if r.status_code != 200:
        error_text = f'Проблемы с получением токена, ответ: {r.status_code} {r.text}'
        logger.error(f'Ошибка при получении токена {error_text}')
        raise AuthorizationError(error_text)

    logger.info(f'Токен для пользователя {MONITORING_USER_LOGIN} получен')
    return r.json()['access_token']

