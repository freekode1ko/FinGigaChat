from pathlib import Path

import pandas as pd
from aiogram import types, F
from aiogram.utils.media_group import MediaGroupBuilder

from constants import constants
from db.api.industry import industry_db, get_industry_analytic_files
from handlers.analytics.handler import router
from keyboards.analytics.industry import callbacks, constructors as keyboards
from log.bot_logger import user_logger


@router.callback_query(callbacks.Menu.filter(
    F.menu == callbacks.MenuEnum.main_menu
))
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.Menu) -> None:
    """
    Получение меню Отраслевая аналитика

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит информацию, какое menu, какая отрасль industry_id, какой тип отрасли industry_type
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    industry_df = await industry_db.get_all()
    industry_df['type'] = callbacks.IndustryTypes.default
    industry_df['name'] = industry_df['name'].str.capitalize()
    other_buttons = pd.DataFrame(
        [
            {
                'id': 0,
                'name': 'Прочие',
                'type': callbacks.IndustryTypes.other,
            },
            {
                'id': 0,
                'name': 'Общий комментарий по отраслям',
                'type': callbacks.IndustryTypes.general_comments,
            },
        ],
    )
    industry_df = pd.concat([industry_df, other_buttons])

    keyboard = keyboards.get_menu_kb(industry_df)
    msg_text = 'Отраслевая аналитика'
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.Menu.filter(
    F.menu == callbacks.MenuEnum.get_industry_anal
))
async def get_industry_analytics(callback_query: types.CallbackQuery, callback_data: callbacks.Menu) -> None:
    """
    Выдача файлов с аналитикой по отраслям

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит информацию, какое menu, какая отрасль industry_id, какой тип отрасли industry_type
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    msg_text = 'Отраслевая аналитика\n'

    match callback_data.industry_type:
        case callbacks.IndustryTypes.other:
            msg_text += '<b>Прочие</b>\n'
        case callbacks.IndustryTypes.general_comments:
            msg_text += '<b>Общий комментарии по отраслям</b>\n'
        case _:
            industry_info = await industry_db.get(callback_data.industry_id)
            msg_text += f'<b>{industry_info["name"].capitalize()}</b>\n'

    files = await get_industry_analytic_files(callback_data.industry_id, callback_data.industry_type)
    files = [Path(f.file_path) for f in files]
    if files:
        await callback_query.message.answer(msg_text, protect_content=True, parse_mode='HTML')

        for i in range(0, len(files), constants.TELEGRAM_MAX_MEDIA_ITEMS):
            media_group = MediaGroupBuilder()
            for fpath in files[i: i + constants.TELEGRAM_MAX_MEDIA_ITEMS]:
                if fpath.exists():
                    media_group.add_document(media=types.FSInputFile(fpath))

            await callback_query.message.answer_media_group(media_group.build(), protect_content=True)
    else:
        msg_text += 'Функционал появится позднее'
        await callback_query.message.answer(msg_text, protect_content=True, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
