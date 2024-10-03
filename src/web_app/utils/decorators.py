from functools import wraps

import jinja2.exceptions

from utils.templates import templates


def handle_jinja_template_exceptions(func):
    """Получить темплейт если ничего не найдено"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        """Враппер"""
        try:
            return await func(*args, **kwargs)
        except jinja2.exceptions.TemplateError:
            return templates.TemplateResponse("not_found.html", {"request": kwargs.get('request')})
    return wrapper
