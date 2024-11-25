import sqlalchemy as sa

from models import models
from migrations.data.new_structure_for_telegram_subs import bot_telegram_group


data = [
    # ------------------- GROUP 1 ---------------------
    {
        'name': bot_telegram_group.data[0]['name'],
        'display_order': 1,
        'group_id': sa.select(models.TelegramGroup.id).where(
            models.TelegramGroup.name == bot_telegram_group.data[0]['name'],
        ).limit(1),
    },
    # ------------------- GROUP 2 ---------------------
    {
        'name': bot_telegram_group.data[1]['name'],
        'display_order': 1,
        'group_id': sa.select(models.TelegramGroup.id).where(
            models.TelegramGroup.name == bot_telegram_group.data[1]['name'],
        ).limit(1),
    },
]
