"""
Реализует два интерфейса взаимодействия с таблицей telegram_channel.

Один интерфейс работает с объектами sqlalchemy.
Второй интерфейс предоставляет возможность получения новостей
"""
from db import models
from db.api.base_crud import BaseCRUD
from db.api.subject_interface import SubjectInterface
from log.bot_logger import logger


class TelegramChannelCRUD(BaseCRUD[models.TelegramChannel]):
    """Класс, который создает объекты для взаимодействия с таблицей models.TelegramChannel"""


telegram_channel_db = TelegramChannelCRUD(models.TelegramChannel, models.TelegramChannel.id, logger)
telegram_channel_article_db = SubjectInterface(
    models.TelegramChannel,
    None,
    None,
    models.RelationTelegramArticle.article,
    models.RelationTelegramArticle,
    -1,
)
