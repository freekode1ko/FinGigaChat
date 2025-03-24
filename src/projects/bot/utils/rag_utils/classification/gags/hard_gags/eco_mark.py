"""Формирование заглушек по макроэкономическим показателям"""
from typing import Any

import pandas as pd
from aiogram import Bot

from constants.constants import DEFAULT_RAG_ANSWER
from constants.texts import texts_manager
from db import database
from log.bot_logger import logger


def get_key_eco_mark_line(name: str) -> dict[str, Any] | None:
    """Получить строку с показателями по имени."""
    key_eco_table = pd.read_sql_query('SELECT * FROM key_eco', con=database.engine)
    key_eco_table = key_eco_table.drop(columns=['id', 'alias'])
    filtered_df = key_eco_table[key_eco_table['name'].str.contains(name, case=False, regex=True)]

    if not filtered_df.empty:
        title = filtered_df.iloc[0]['name']
        values = filtered_df.drop(columns=['name']).to_dict(orient='records')
        return {'title': title, 'values': values}


async def send_eco_marks(bot: Bot, chat_id: int, text_cnst: str, name: str):
    """Отправка сообщения с макроэкономическим показателем."""
    try:
        eco_mark_line = get_key_eco_mark_line(name)
        if eco_mark_line is None:
            msg = f'Не были получены данные из key_eco для показателя "{name}"'
            raise ValueError(msg)

        txt_data = ''
        for line_values in eco_mark_line['values']:
            txt_data += '\n'.join(f'•  {value} ({year})' for year, value in line_values.items())
        text = f'{text_cnst}\n\n<b>{eco_mark_line["title"]}</b>\n{txt_data}'

    except Exception as e:
        logger.exception(e)
        text = DEFAULT_RAG_ANSWER

    await bot.send_message(chat_id, text, parse_mode='HTML', protect_content=texts_manager.PROTECT_CONTENT)
    return text
