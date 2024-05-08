import sqlalchemy as sa

from db import models
from migrations.data.new_structure_for_telegram_subs import bot_telegram_section


data = [
    # --------------- Общеновостные --------------------
    {
        'name': '🔥Full-Time Trading',
        'link': 'https://t.me/+qKeau08SQjs2M2My/',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[0]['name'],
        ).limit(1),
    },
    {
        'name': 'РИА Новости',
        'link': 'https://t.me/rian_ru/',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[0]['name'],
        ).limit(1),
    },
    {
        'name': 'Раньше всех. Ну почти.',
        'link': 'https://t.me/bbbreaking/',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[0]['name'],
        ).limit(1),
    },
    {
        'name': 'Mash',
        'link': 'https://t.me/breakingmash/',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[0]['name'],
        ).limit(1),
    },
    {
        'name': 'Осторожно, новости',
        'link': 'https://t.me/ostorozhno_novosti/',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[0]['name'],
        ).limit(1),
    },
    # --------------- Финансовые --------------------
    {
        'name': 'MarketTwits',
        'link': 'https://t.me/markettwits',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[1]['name'],
        ).limit(1),
    },
    {
        'name': 'MMI',
        'link': 'https://t.me/russianmacro',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[1]['name'],
        ).limit(1),
    },
    {
        'name': 'headlines',
        'link': 'https://t.me/headlines_for_traders',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[1]['name'],
        ).limit(1),
    },
    {
        'name': 'РБК',
        'link': 'https://t.me/rbc_news',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[1]['name'],
        ).limit(1),
    },
    {
        'name': 'Банкста',
        'link': 'https://t.me/banksta',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[1]['name'],
        ).limit(1),
    },
    {
        'name': 'Forbes Russia',
        'link': 'https://t.me/forbesrussia',
        'section_id': sa.select(models.TelegramSection.id).where(
            models.TelegramSection.name == bot_telegram_section.data[1]['name'],
        ).limit(1),
    },
]
