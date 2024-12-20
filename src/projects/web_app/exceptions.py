class ApplicationError(Exception):
    """Базовое исключение для ошибок в приложении"""
    pass


class InfrastructureError(Exception):
    """Базовое исключение для ошибок в сторонних системах: FS, БД, API"""
    pass
