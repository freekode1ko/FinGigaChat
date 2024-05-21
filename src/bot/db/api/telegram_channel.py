from db import models
from db.api.base_crud import BaseCRUD
from log.bot_logger import logger


class TelegramChannelCRUD(BaseCRUD[models.TelegramChannel]):
    """Класс, который создает объекты для взаимодействия с таблицей models.TelegramChannel"""


telegram_channel_db = TelegramChannelCRUD(models.TelegramChannel, models.TelegramChannel.id, logger)
