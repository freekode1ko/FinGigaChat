"""API для работы с настройками приложения"""
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_current_admin
from constants import texts

from .schemas import SettingsRead, SettingsUpdate


router = APIRouter(tags=['settings'])


@router.get(
        '/',
        response_model=list[SettingsRead],
        dependencies=[Depends(get_current_admin)],
)
async def get_app_settings():
    """
    *Только для администраторов*\n
    Получить список доступных настроек приложения
    """
    return await texts.texts_manager.get_all()


@router.post(
        '/{key}',
        dependencies=[Depends(get_current_admin)],
)
async def set_app_setting(
    key: str,
    data: SettingsUpdate,
):
    """
    *Только для администраторов*\n
    Установить новое значение настройке приложения
    """
    try:
        await texts.texts_manager.set(key, data.value)
    except AttributeError:
        raise HTTPException(status_code=400, detail='Проверьте правильность введенных данных')
