import uuid
from pathlib import Path
from dataclasses import dataclass

import aiofiles
from fastapi import UploadFile

from exceptions import ApplicationError, InfrastructureError


@dataclass(frozen=True, slots=True)
class File:
    """
    Объект файла после загрузки в систему.

    :Path path: Путь к файлу в системе
    :str filename: Имя файла
    :int size: Размер файла в байтах
    """
    path: Path
    filename: str
    size: int


class FileSizeError(ApplicationError):
    """Ошибка при превышении допустимого размера файла"""
    pass


class FileTypeError(ApplicationError):
    """Ошибка при недопустимом расширении файла"""
    pass


class FileNameError(ApplicationError):
    """Ошибка при попытке сохранить файл с уже существующим именем"""
    pass


class FileSaveError(InfrastructureError):
    """Ошибка сохранения файла на сервере"""
    pass


async def upload_file(
        file: UploadFile,
        dest: Path | str,
        max_size: int,
        allowed_types: tuple[str],
) -> File:
    """
    Функция для сохранения файла на сервере.

    :UploadFile file: Объект файла, загружаемого через FastAPI
    :Union[Path, str] dest: Путь для сохранения файла
    :int max_size: Максимально допустимый размер файла
    :tuple[str] allowed_types: Кортеж с допустимыми для сохранения MIME-типами
    """
    if file.content_type not in allowed_types:
        raise FileTypeError('Недопустимое расширение файла')

    filepath = Path(dest) / file.filename
    if filepath.exists():
        raise FileNameError('Измените название файла')

    size = 0
    try:
        async with aiofiles.open(filepath, 'wb') as out_file:
            while content := await file.read(1024):
                size += len(content)
                if size > max_size:
                    raise FileSizeError('Файл слишком большой')
                await out_file.write(content)
    except Exception:
        raise FileSaveError('Ошибка при попытке сохранить файл')

    return File(filepath, file.filename, size)
