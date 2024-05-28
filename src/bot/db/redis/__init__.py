"""Пакет по работе с Redis."""

from db.redis.user_dialog import (
    del_dialog,
    get_dialog,
    get_last_user_msg,
    update_dialog
)

__all__ = [
    'del_dialog',
    'get_dialog',
    'get_last_user_msg',
    'update_dialog'
]
