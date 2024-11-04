"""Значения по умолчанию для всех констант из Redis, которые используются в WebApp"""

DEFAULT_VALUES = {
    # AUTH
    'AUTH_EMAIL_TEXT': (
        'Добрый день!\n\n'
        'Вы получили данное письмо, потому что указали данный адрес при авторизации в веб-версии терминала AI-помощника Банкира.\n\n'
        'Код для завершения авторизации:\n\n{code}\n'
        'Никому не сообщайте этот код.'
    ),

    # WATERMARK
    'FONT_TYPE': 'Helvetica',
    'FONT_SIZE': 20,
    'ROTATION': 45,
    'FONT_COLOR_ALPHA': 0.3,
    'VERTICAL_REPETITIONS': 3,
    'HORIZONTAL_REPETITIONS': 3,
}
