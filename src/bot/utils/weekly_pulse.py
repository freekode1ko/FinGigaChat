from aiogram import types, Bot

from configs import config
from constants.constants import sample_of_img_title
from db import parser_source


def __get_weekly_pulse_parse_datetime() -> str:
    source_name = 'Weekly Pulse'
    last_update_time = parser_source.get_source_last_update_datetime(source_name=source_name)
    return last_update_time.strftime(config.BASE_DATE_FORMAT)


async def key_rate_dynamics_table(bot: Bot, chat_id: int) -> None:
    title = 'Прогноз динамики ключевой ставки'
    data_source = 'SberCIB Investment Research'
    png_path = config.PATH_TO_SOURCES / 'weeklies' / 'key_rate_dynamics_table.png'

    parse_datetime = __get_weekly_pulse_parse_datetime()

    title = sample_of_img_title.format(title, data_source, parse_datetime)
    photo = types.FSInputFile(png_path)
    await bot.send_photo(chat_id, photo, caption=title, parse_mode='HTML', protect_content=True)


async def exc_rate_prediction_table(bot: Bot, chat_id: int) -> None:
    title = 'Прогноз валютных курсов'
    data_source = 'SberCIB Investment Research'
    png_path = config.PATH_TO_SOURCES / 'weeklies' / 'exc_rate_prediction_table.png'

    parse_datetime = __get_weekly_pulse_parse_datetime()

    title = sample_of_img_title.format(title, data_source, parse_datetime)
    photo = types.FSInputFile(png_path)
    await bot.send_photo(chat_id, photo, caption=title, parse_mode='HTML', protect_content=True)
