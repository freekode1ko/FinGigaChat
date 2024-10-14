"""Модуль с текстовками регистрации."""
from pydantic_settings import BaseSettings

from configs.config import STATE_TIMEOUT


class RegistrationTexts(BaseSettings):
    """Класс для хранения текстовок при регистрации пользователя."""

    REGISTRATION_START: str = (
        'Рады приветствовать Вас в AI-помощнике банкира!\n'
        'Для того, чтобы начать пользоваться ботом нужно пройти идентификацию.\n\n'
        'Введите корпоративную почту, на нее будет выслан код для завершения регистрации.\n'
        f'❗ Код действителен не более {STATE_TIMEOUT.total_seconds() // 60} минут.'
    )

    REGISTRATION_EMAIL_TEXT: str = (
        'Добрый день!\n\n'
        'Вы получили данное письмо, потому что указали данный адрес в AI-помощнике Банкира.\n\n'
        'Код для завершения регистрации:\n\n{code}\n'
        'Никому не сообщайте этот код.'
    )

    REGISTRATION_REQUEST_CODE: str = 'Для завершения регистрации, введите код, отправленный вам на почту.'

    REGISTRATION_WELCOME: str = 'Добро пожаловать, {user_name}!'

    REGISTRATION_ERROR: str = 'Во время авторизации произошла ошибка, попробуйте позже.'

    REGISTRATION_NOT_UNIQUE_EMAIL: str = (
        'Пользователь с такой почтой уже существует! '
        'Нажмите /start, чтобы попробовать еще раз.'
    )

    REGISTRATION_NOT_WHITELIST_EMAIL: str = (
        'Для продолжения регистрации, пожалуйста, '
        'свяжитесь с командой проекта: @korolkov_m'
    )

    REGISTRATION_NOT_CORPORATE_EMAIL: str = 'Указана не корпоративная почта'

    REGISTRATION_NOT_CORRECT_CODE: str = 'Вы ввели некорректный регистрационный код. Осталось {attempts} попытки.'

    REGISTRATION_NOT_ATTEMPTS_LEFT: str = 'Вы истратили все попытки. Попробуйте заново, используя команду /start.'
