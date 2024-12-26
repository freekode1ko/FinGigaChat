"""API для работы с продуктами"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from constants import constants, enums
from api.dependencies import get_current_admin, get_repository
from db.models import CommodityResearch
from db.repository import CommodityRepository
from utils.files import upload_file

from .schemas import CommodityRead


router = APIRouter(tags=['commodities'])


@router.get(
        '/',
        response_model=list[CommodityRead],
        dependencies=[Depends(get_current_admin)],
)
async def get_commodities(
    commodity_repository: Annotated[CommodityRepository, Depends(get_repository(CommodityRepository))],
):
    """
    *Только для администраторов*\n
    Получить список всех commodities вместе со списком исследований
    """
    return await commodity_repository.get_with_researches()


@router.post(
    '/{commodity_id}/researches',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def create_research(
    commodity_id: int,
    commodity_repository: Annotated[CommodityRepository, Depends(get_repository(CommodityRepository))],
    title: str | None = Form(None),
    text: str = Form(...),
    file: UploadFile | None = File(None),
) -> None:
    """
    *Только для администраторов*\n
    Загрузить исследование для commodity\n
    Если файл не загружен, то в базе будет сохранен пустой путь
    """
    commodity = await commodity_repository.get_by_id_with_researches(commodity_id)
    if commodity is None:
        raise HTTPException(status_code=404, detail='Такой commodity не найден')
    if file is not None:
        saved_file = await upload_file(
            file,
            constants.PATH_TO_COMMODITY_REPORTS,
            constants.MAX_FILE_SIZE,
            (enums.MimeType.PDF.value,),
        )
    else:
        saved_file = None
    research = CommodityResearch(
        title=title,
        text=text,
        file_name=saved_file.filename if saved_file else None,
    )
    await commodity_repository.add_commodity_research(commodity, research)
