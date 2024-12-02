import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile


class FileSizeError(Exception):
    """Ошибка при превышении допустимого размера файла"""
    pass


class FileTypeError(Exception):
    """Ошибка при недопустимом расширении файла"""
    pass


class FileSaveError(Exception):
    """Ошибка сохранения файла на сервере"""
    pass


async def upload_file(
        file: UploadFile,
        dest: Path | str,
        max_size: int,
        allowed_types: tuple[str],
) -> Path:
    if file.content_type not in allowed_types:
        raise FileTypeError('Недопустимое расширение файла')
    filename = f'{uuid.uuid4().hex}_{file.filename}'
    filepath = Path(dest) / filename
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
    return filepath
