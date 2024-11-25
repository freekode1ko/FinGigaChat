"""Файл хендлеров продуктов"""

import os
from pathlib import Path

import aiogram.exceptions
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware

import configs.config
from constants import enums
from constants.texts import texts_manager
from db import models
from db.api.product import product_db
from handlers.products import callbacks
from handlers.products import keyboards
from log.bot_logger import user_logger
from utils.base import send_full_copy_of_message, send_or_edit, send_pdf
from utils.decorators import has_access_to_feature

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

    match callback_query.message.content_type:
        case types.ContentType.TEXT:
            await callback_query.message.edit_text(text='Завершена работа с меню "продукты"')
        case types.ContentType.DOCUMENT:
            try:
                await callback_query.message.delete()
            except aiogram.exceptions.TelegramBadRequest:
                pass
            await callback_query.message.answer(text='Завершена работа с меню "продукты"')


async def main_menu(message: types.CallbackQuery | types.Message) -> None:
    """
    Формирует меню продукты

    :param message: types.CallbackQuery | types.Message
    """
    root = await product_db.get_root()
    keyboard = keyboards.get_menu_kb(root.children)
    await send_or_edit(message, root.description, keyboard)


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
@has_access_to_feature(enums.FeatureType.products_menu)
async def main_menu_command(message: types.Message) -> None:
    """
    Получение меню продукты

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    await main_menu(message)


@router.callback_query(callbacks.ProductsMenuData.filter(
    F.menu == callbacks.ProductsMenusEnum.group_products,
))
async def get_group_products(
        tg_obj: types.CallbackQuery | types.Message,
        callback_data: callbacks.ProductsMenuData,
        product_id: int | None = None,
) -> None:
    """
    Получение меню продукты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит информацию о текущем меню, группе, продукте, формате выдачи предложений
    :param product_id: Айди Product, если вызов функции из Function Calling
    """
    chat_id, user_msg = (tg_obj.chat.id, tg_obj.text
                         if isinstance(tg_obj, types.Message)
                         else tg_obj.message.chat.id, callback_data.pack())
    full_name = tg_obj.from_user.full_name
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

    if isinstance(tg_obj, types.Message) and product_id:
        message = tg_obj
        product_id = product_id
    else:  # isinstance(callback_query, types.CallbackQuery) and not product_id:
        message = tg_obj.message
        product_id = callback_data.product_id

    product_info = await product_db.get(product_id)
    sub_products = product_info.children

    if not sub_products:
        resend = await get_product_documents(
            tg_obj,
            product_info,
            resend_message=isinstance(tg_obj, types.CallbackQuery)
        )

        if isinstance(tg_obj, types.Message) and resend:
            parent = await product_db.get(product_info.parent.id)
            await message.answer(
                parent.description,
                reply_markup=keyboards.get_sub_menu_kb(parent.children, parent, callback_data),
                parse_mode='HTML',
            )
    else:
        keyboard = keyboards.get_sub_menu_kb(sub_products, product_info, callback_data)
        msg_text = product_info.description
        if product_info.documents and (fpath := configs.config.PROJECT_DIR / product_info.documents[0].file_path).exists():
            await message.answer_document(
                document=types.FSInputFile(fpath),
                caption=msg_text,
                parse_mode='HTML',
                reply_markup=keyboard,
            )
        else:
            await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML')

        try:
            await message.delete()
        except aiogram.exceptions.TelegramBadRequest:
            pass
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callbacks.ProductsMenuData.filter(
    F.menu == callbacks.ProductsMenusEnum.get_product_documents,
))
async def get_product_documents_callback(callback_query: types.CallbackQuery, callback_data: callbacks.ProductsMenuData) -> None:
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
    await get_product_documents(callback_query, product_info)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def get_product_documents(
        callback_query: types.CallbackQuery | types.Message,
        product: models.Product,
        resend_message: bool
) -> bool:
    """
    Получение продуктовых предложений

    Отправляет копию меню в конце, если были отправлены продуктовые предложения

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param product: содержит информацию о продукте, формате выдачи предложений
    :param resend_message: Переотправлять ли сообщение повторно
    :return: Отправлены ли были документы
    """
    documents = list(product.documents)

    msg_text = product.description

    if isinstance(callback_query, types.CallbackQuery):
        message = callback_query.message
    else:
        message = callback_query

    match product.send_documents_format_type:
        case enums.FormatType.group_files:
            pdf_files = [Path(i.file_path) for i in documents]
            if not await send_pdf(message, pdf_files, msg_text, protect_content=texts_manager.PROTECT_CONTENT):
                msg_text += texts_manager.COMMON_FEATURE_WILL_APPEAR
                await message.answer(msg_text, parse_mode='HTML')
            else:
                if resend_message:
                    await send_full_copy_of_message(callback_query)
                return True
        case enums.FormatType.individual_messages:
            if not documents:
                msg_text += texts_manager.COMMON_FEATURE_WILL_APPEAR

            await message.answer(msg_text, parse_mode='HTML')

            for document in documents:
                document_msg_text = ''
                if document.name:
                    document_msg_text += f'<b>{document.name}</b>\n\n'
                if document.description:
                    document_msg_text += document.description

                if document_msg_text:
                    await message.answer(document_msg_text, parse_mode='HTML')

                if os.path.exists(document.file_path):
                    await message.bot.send_chat_action(message.chat.id, 'upload_document')
                    await message.answer_document(types.FSInputFile(document.file_path))

            if documents:
                if resend_message:
                    await send_full_copy_of_message(callback_query)
                return True
    return False
