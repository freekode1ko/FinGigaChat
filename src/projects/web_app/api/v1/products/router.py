"""API для работы с продуктами"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status

from constants import constants, enums
from api.dependencies import get_current_admin, get_repository
from db.models import ProductDocument, Product
from db.mapper import pydantic_to_sqlalchemy
from db.repository import ProductRepository, ProductDocumentRepository
from utils.files import upload_file

from .schemas import ProductRead, ShortProductRead, ProductUpdate, ProductCreate


router = APIRouter(tags=['products'])


@router.get(
        '/tree',
        response_model=list[ProductRead],
        dependencies=[Depends(get_current_admin)],
)
async def get_products_tree(
    product_repository: Annotated[ProductRepository, Depends(get_repository(ProductRepository))],
):
    """
    *Только для администраторов*\n
    Получить список всех продуктов в виде древовидной структуры
    """
    return await product_repository.get_products_tree()


@router.get(
        '/',
        response_model=list[ShortProductRead],
        dependencies=[Depends(get_current_admin)],
)
async def get_products(
    product_repository: Annotated[ProductRepository, Depends(get_repository(ProductRepository))],
):
    """
    *Только для администраторов*\n
    Получить список всех продуктов в упрощенном формате (без дочерних продуктов и документов)
    """
    return await product_repository.get_list()


@router.patch(
        '/{product_id}',
        dependencies=[Depends(get_current_admin)],
)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    product_repository: Annotated[ProductRepository, Depends(get_repository(ProductRepository))],
):
    """
    *Только для администраторов*\n
    Изменить продукт
    """
    product = await product_repository.get_by_pk(product_id)
    if product is None:
        raise HTTPException(status_code=404)
    updated_product = pydantic_to_sqlalchemy(product_data, Product, product)
    await product_repository.update(updated_product)


@router.post(
        '/',
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(get_current_admin)],
)
async def create_product(
    product_data: ProductCreate,
    product_repository: Annotated[ProductRepository, Depends(get_repository(ProductRepository))],
):
    """
    *Только для администраторов*\n
    Создать продукт
    """
    product = pydantic_to_sqlalchemy(product_data, Product)
    await product_repository.create(product)


@router.post(
    '/{product_id}/documents',
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
)
async def create_document(
    product_id: int,
    name: str = Form(...),
    description: str | None = Form(None),
    file: UploadFile = File(...),
    document_repository: ProductDocumentRepository = Depends(get_repository(ProductDocumentRepository)),
) -> None:
    """
    *Только для администраторов*\n
    Загрузить документ для продукта
    """
    filepath = await upload_file(
        file,
        constants.PATH_TO_PRODUCTS,
        constants.MAX_PDF_SIZE,
        (enums.MimeType.PDF.value,),
    )
    document = ProductDocument(
        name=name,
        description=description,
        product_id=product_id,
        file_path=str(filepath),
    )
    await document_repository.create(document)
