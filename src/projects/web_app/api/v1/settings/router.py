"""API для работы с настройками приложения"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_current_admin, get_repository
from db.repository import SettingsAliasesRepository
from constants import texts

from .schemas import SettingsRead, SettingsUpdate


router = APIRouter(tags=['settings'])


@router.get(
        '/',
        response_model=list[SettingsRead],
        dependencies=[Depends(get_current_admin)],
)
async def get_app_settings(
    settings_repository: Annotated[SettingsAliasesRepository, Depends(get_repository(SettingsAliasesRepository))],
):
    """
    *Только для администраторов*\n
    Получить список доступных настроек приложения
    """
    allowed_settings = await settings_repository.get_list()
    return [
        SettingsRead(key=setting.key, value=await texts.texts_manager.get(setting.key), name=setting.name)
        for setting in allowed_settings
    ]


@router.post(
        '/{key}',
        dependencies=[Depends(get_current_admin)],
)
async def set_app_setting(
    key: str,
    data: SettingsUpdate,
    settings_repository: Annotated[SettingsAliasesRepository, Depends(get_repository(SettingsAliasesRepository))]
):
    """
    *Только для администраторов*\n
    Установить новое значение настройке приложения
    """
    if not await settings_repository.get_by_key(key):
        raise HTTPException(status_code=400, detail='Проверьте правильность введенных данных')
    await texts.texts_manager.set(key, data.value)
