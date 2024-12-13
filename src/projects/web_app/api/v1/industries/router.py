"""API для работы с отраслями"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from constants import constants, enums
from api.dependencies import get_current_admin, get_repository
from db.models import IndustryDocuments, Industry
from db.mapper import pydantic_to_sqlalchemy
from db.repository import IndustryRepository, IndustryDocumentRepository
from utils.files import upload_file

from .schemas import IndustryRead, IndustryUpdate, IndustryCreate


router = APIRouter(tags=['industries'])


@router.get(
    '/',
    response_model=list[IndustryRead],
    dependencies=[Depends(get_current_admin)],
)
async def get_industries(
    industry_repository: Annotated[IndustryRepository, Depends(get_repository(IndustryRepository))],
):
    """
    *Только для администраторов*
    Получить список всех отраслей
    """
    return await industry_repository.get_list_with_documents()


@router.get(
    '/{industry_id}',
    response_model=IndustryRead,
    dependencies=[Depends(get_current_admin)],
)
async def get_industry(
    industry_id: int,
    industry_repository: Annotated[IndustryRepository, Depends(get_repository(IndustryRepository))],
):
    """
    *Только для администраторов*
    Получить отрасль по ID
    """
    if (industry := await industry_repository.get_by_pk_with_documents(industry_id)) is None:
        raise HTTPException(status_code=404)
    return industry


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def create_industry(
    industry_data: IndustryCreate,
    industry_repository: Annotated[IndustryRepository, Depends(get_repository(IndustryRepository))],
):
    """
    *Только для администраторов*
    Создать отрасль
    """
    industry = pydantic_to_sqlalchemy(industry_data, Industry)
    await industry_repository.create(industry)


@router.patch(
    '/{industry_id}',
    dependencies=[Depends(get_current_admin)],
)
async def update_industry(
    industry_id: int,
    industry_data: IndustryUpdate,
    industry_repository: Annotated[IndustryRepository, Depends(get_repository(IndustryRepository))],
):
    """
    *Только для администраторов*
    Изменить отрасль
    """
    if (industry := await industry_repository.get_by_pk(industry_id)) is None:
        raise HTTPException(status_code=404)
    updated_industry = pydantic_to_sqlalchemy(industry_data, Industry, industry)
    await industry_repository.update(updated_industry)


@router.delete(
    '/{industry_id}',
    dependencies=[Depends(get_current_admin)],
)
async def delete_industry(
    industry_id: int,
    industry_repository: Annotated[IndustryRepository, Depends(get_repository(IndustryRepository))],
):
    """
    *Только для администраторов*
    Удалить отрасль
    """
    if (industry := await industry_repository.get_by_pk(industry_id)) is None:
        raise HTTPException(status_code=404)
    await industry_repository.delete(industry)


@router.post(
    '/{industry_id}/documents',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def create_document(
    industry_id: int,
    industry_repository: Annotated[IndustryRepository, Depends(get_repository(IndustryRepository))],
    industry_document_repository: Annotated[IndustryDocumentRepository, Depends(get_repository(IndustryDocumentRepository))],
    name: str = Form(...),
    file: UploadFile = File(...),
) -> None:
    """
    *Только для администраторов*
    Загрузить документ для отрасли
    """
    if await industry_repository.get_by_pk(industry_id) is None:
        raise HTTPException(status_code=404)
    saved_file = await upload_file(
        file,
        constants.PATH_TO_INDUSTRIES,
        constants.MAX_FILE_SIZE,
        (enums.MimeType.PDF.value,),
    )
    document = IndustryDocuments(
        name=name,
        industry_id=industry_id,
        file_path=str(saved_file.path),
    )
    await industry_document_repository.create(document)
