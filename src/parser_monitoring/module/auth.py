"""Аутентификация в сервисе мониторинга"""
import requests
from requests import exceptions

from configs.config import MONITORING_API_LOGIN_URL, MONITORING_API_PASSWORD, MONITORING_API_USER
from log.logger_base import logger


def get_access_token() -> str:
    """Получение токена доступа к мониторингу."""
    logger.info('Получение токена доступа')
    try:
        r = requests.post(
            url=MONITORING_API_LOGIN_URL,
            data={'username': MONITORING_API_USER, 'password': MONITORING_API_PASSWORD}
        )
        if r.status_code == 200:
            logger.info(f'Токен для пользователя {MONITORING_API_USER} получен')
            return r.json()['access_token']
    except (exceptions.RequestException, exceptions.ConnectionError) as e:
        logger.error(f'Ошибка при получении токена {e}')
        raise
