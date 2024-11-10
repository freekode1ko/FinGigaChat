import hashlib
import hmac
import time
from urllib.parse import parse_qs

from config import BOT_API_TOKEN
from api.v1.auth.schemas import TelegramData
from constants.constants import TELEGRAM_DATA_VALIDITY_PERIOD


TELEGRAM_DATA_SOURCE = 'WebAppData'


def validate_telegram_data(data: TelegramData) -> bool:
    """
    Функция для проверки валидности данных пользователя
    Telegram, полученных по API.

    :param TelegramData telegram_data: Объект с данными пользователя
    :return: True, если данные валидны, иначе False
    """
    parsed_data = parse_qs(data.data)
    if time.time() - int(parsed_data.get('auth_date', [0])[0]) > TELEGRAM_DATA_VALIDITY_PERIOD:
        return False
    check_hash = parsed_data.pop('hash', [None])[0]
    if not check_hash:
        return False

    data_check_arr = []
    for key, value in parsed_data.items():
        data_check_arr.append(f'{key}={value[0]}')
    data_check_arr.sort()
    data_check_string = '\n'.join(data_check_arr)

    secret_key = hmac.new(TELEGRAM_DATA_SOURCE.encode(), BOT_API_TOKEN.encode(), hashlib.sha256).digest()
    hmac_string = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return hmac_string == check_hash
