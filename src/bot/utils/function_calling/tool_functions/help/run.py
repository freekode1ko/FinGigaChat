from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from handlers.common import HelpButton
from utils.function_calling.tool_functions.utils import parse_runnable_config


@tool
async def get_help_function(runnable_config: RunnableConfig) -> str:
    """Если пользователь просит помощи и не понимает что делать, то эта функция отправляет ему сообщение с руководством.

    return:
        (str): сообщение с руководством.
    """
    runnable_config = parse_runnable_config(runnable_config)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(
        text='Показать',
        callback_data=HelpButton().pack())
    )

    await runnable_config.message.answer(
        "Описание бота",
        reply_markup=keyboard.as_markup()
    )
