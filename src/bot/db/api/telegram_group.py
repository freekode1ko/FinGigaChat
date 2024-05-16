from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class TelegramGroupCRUD(BaseCRUD[models.TelegramGroup]):
    """Класс, который создает объекты для взаимодействия с таблицей models.TelegramGroup"""


telegram_group_db = TelegramGroupCRUD(models.TelegramGroup, models.TelegramGroup.display_order, logger)
