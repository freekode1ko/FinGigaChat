"""Файл хендлеров продуктов"""

import os
from pathlib import Path
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware

from constants.products import state_support
from db.api.product import product_db
from db.api.product_document import product_document_db
from db.api.product_group import product_group_db
from handlers.products import callbacks
from handlers.products import keyboards
from log.bot_logger import user_logger
from utils.base import send_full_copy_of_message, send_or_edit, send_pdf, user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(callbacks.ProductsMenuData.filter(
    F.menu == callbacks.ProductsMenusEnum.end_menu,
))
async def menu_end(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню продукты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(text='Завершена работа с меню "продукты"')


async def main_menu(message: types.CallbackQuery | types.Message) -> None:
    """
    Формирует меню продукты

    :param message: types.CallbackQuery | types.Message
    """
    product_groups = await product_group_db.get_all()
    keyboard = keyboards.get_menu_kb(product_groups)
    msg_text = 'Актуальные предложения для клиента'
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(callbacks.ProductsMenuData.filter(
    F.menu == callbacks.ProductsMenusEnum.main_menu,
))
async def main_menu_callback(callback_query: types.CallbackQuery, callback_data: callbacks.ProductsMenuData) -> None:
    """
    Получение меню продукты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит информацию о текущем меню, группе, продукте, формате выдачи предложений
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await main_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callbacks.ProductsMenuData.__prefix__))
async def main_menu_command(message: types.Message) -> None:
    """
    Получение меню продукты

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await main_menu(message)
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(callbacks.ProductsMenuData.filter(
    F.menu == callbacks.ProductsMenusEnum.state_support,
))
async def get_state_support_pdf(callback_query: types.CallbackQuery, callback_data: callbacks.ProductsMenuData) -> None:
    """
    Получение pdf файлов по господдержке

    Отправляет копию меню в конце, если были отправлены файлы

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит информацию о текущем меню, группе, продукте, формате выдачи предложений
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    msg_text = state_support.TITLE
    pdf_files = list(state_support.DATA_ROOT_PATH.iterdir())
    await send_pdf(callback_query, pdf_files, msg_text)
    await send_full_copy_of_message(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.ProductsMenuData.filter(
    F.menu == callbacks.ProductsMenusEnum.group_products,
))
async def get_group_products(
        callback_query: types.CallbackQuery,
        callback_data: callbacks.ProductsMenuData,
        back_callback_data: Optional[str] = None,
) -> None:
    """
    Получение меню продукты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит информацию о текущем меню, группе, продукте, формате выдачи предложений
    :param back_callback_data: callback_data для кнопки назад
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    group_info = await product_group_db.get(callback_data.group_id)
    products = await product_db.get_all_by_group_id(group_id=callback_data.group_id)

    keyboard = keyboards.get_sub_menu_kb(products, callback_data.format_type, back_callback_data)
    msg_text = group_info.description
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.ProductsMenuData.filter(
    F.menu == callbacks.ProductsMenusEnum.get_product_documents,
))
async def get_product_documents(callback_query: types.CallbackQuery, callback_data: callbacks.ProductsMenuData) -> None:
    """
    Получение продуктовых предложений

    Отправляет копию меню в конце, если были отправлены продуктовые предложения

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит информацию о текущем меню, группе, продукте, формате выдачи предложений
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    product_info = await product_db.get(callback_data.product_id)
    documents = await product_document_db.get_all_by_product_id(product_id=callback_data.product_id)

    msg_text = product_info.description

    match callback_data.format_type:
        case callbacks.FormatType.group_files:
            pdf_files = [Path(i.file_path) for i in documents]
            if not await send_pdf(callback_query, pdf_files, msg_text):
                msg_text += '\nФункционал появится позднее'
                await callback_query.message.answer(msg_text, parse_mode='HTML')
            else:
                await send_full_copy_of_message(callback_query)
        case callbacks.FormatType.individual_messages:
            if not documents:
                msg_text += '\nФункционал появится позднее'

            await callback_query.message.answer(msg_text, parse_mode='HTML')

            for document in documents:
                document_msg_text = ''
                if document.name:
                    document_msg_text += f'<b>{document.name}</b>\n\n'
                if document.description:
                    document_msg_text += document.description

                if document_msg_text:
                    await callback_query.message.answer(document_msg_text, parse_mode='HTML')

                if os.path.exists(document.file_path):
                    await callback_query.message.answer_document(types.FSInputFile(document.file_path))

            if documents:
                await send_full_copy_of_message(callback_query)

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
