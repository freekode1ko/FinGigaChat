import os
import tempfile
from pathlib import Path

from aiogram import types

from constants.constants import PATH_TO_REPORTS
from db.meeting import get_user_email
from utils.bot import bot
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
    add_watermark_cli(
        PATH_TO_REPORTS / f'{report_id}.pdf',
        user_anal_filepath,
        await get_user_email(user_id),
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
