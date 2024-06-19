"""Файл с хендлерами отрасли"""
from pathlib import Path

import pandas as pd
from aiogram import F, types

from db.api.industry import get_industry_analytic_files, industry_db
from handlers.analytics.handler import router
from keyboards.analytics.industry import callbacks, constructors as keyboards
from log.bot_logger import user_logger
from utils.base import send_full_copy_of_message, send_pdf


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
    industry_files = await get_industry_analytic_files(industry_type=callbacks.IndustryTypes.default)
    industry_df['type'] = callbacks.IndustryTypes.default
    industry_df['name'] = industry_df['name'].str.capitalize()
    industry_df = industry_df[industry_df['id'].isin(i.industry_id for i in industry_files)]
    first_buttons = pd.DataFrame(
        [
            {
                'id': None,
                'name': 'Общий комментарий по отраслям',
                'type': callbacks.IndustryTypes.general_comments,
            },
        ],
    )
    last_buttons = pd.DataFrame(
        [
            {
                'id': None,
                'name': 'Прочие',
                'type': callbacks.IndustryTypes.other,
            },
        ],
    )
    industry_df = pd.concat([first_buttons, industry_df.sort_values('display_order'), last_buttons])

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
    files = [p for f in files if (p := Path(f.file_path)).exists()]
    if not await send_pdf(callback_query, files, msg_text, protect_content=True):
        msg_text += '\nФункционал появится позднее'
        await callback_query.message.answer(msg_text, protect_content=True, parse_mode='HTML')
    else:
        await send_full_copy_of_message(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
