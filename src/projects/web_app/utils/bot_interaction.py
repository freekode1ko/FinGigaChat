import os
import tempfile
from pathlib import Path

from aiogram import types

from constants.constants import PATH_TO_REPORTS
from db.meeting import get_user_email
from utils.bot import bot
from constants.texts import texts_manager
from utils.utils import add_watermark_cli


async def send_to_user(func, *args, **kwargs) -> None:
    try:
        await func(*args, **kwargs)
    except Exception as e:
        print(e)


async def send_message_to_user(*args, **kwargs) -> None:
    await send_to_user(bot.send_message, *args, **kwargs)


async def send_document_to_user(*args, **kwargs) -> None:
    await send_to_user(bot.send_document, *args, **kwargs)


async def send_cib_report_to_user(user_id: int, report_id: str) -> None:
    user_anal_filepath = Path(tempfile.gettempdir()) / f'{report_id}_{user_id}_watermarked.pdf'

    # try:
    # TODO: В идеале сходить за константами один раз
    font_type = await texts_manager.get('FONT_TYPE'),
    font_size = await texts_manager.get('FONT_SIZE'),
    rotation = await texts_manager.get('ROTATION'),
    lines_count = await texts_manager.get('VERTICAL_REPETITIONS'),
    word_in_line_count = await texts_manager.get('HORIZONTAL_REPETITIONS'),
    opacity = await texts_manager.get('FONT_COLOR_ALPHA'),
    await add_watermark_cli(
        PATH_TO_REPORTS / f'{report_id}.pdf',
        user_anal_filepath,
        await get_user_email(user_id),
        font_type,
        font_size,
        rotation,
        lines_count,
        word_in_line_count,
        opacity
    )
    # except Exception as e:
    #     print(e)
    # else:
    message_text = ''
    await send_document_to_user(
        document=types.FSInputFile(user_anal_filepath),
        chat_id=user_id,
        caption=message_text,
        parse_mode='HTML',
        protect_content=True
    )
