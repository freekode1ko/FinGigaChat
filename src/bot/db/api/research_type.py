"""
CRUD для взаимодействия с таблицей models.ResearchType.

Позволяет выполнять стандартные операции
"""
from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class ResearchTypeCRUD(BaseCRUD[models.ResearchType]):
    """Класс, который создает объекты для взаимодействия с таблицей models.ResearchType"""


research_type_db = ResearchTypeCRUD(models.ResearchType, models.ResearchType.name, logger)
