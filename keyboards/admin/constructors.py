from aiogram import types
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants.bot import admin as callback_prefixes
from constants.bot import constants
from keyboards.admin import callbacks
from utils.db_api.message_type import message_types


def get_message_types_kb() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру типов сообщений
    Отмена удаляет данное сообщение, если прошло менее 48 часов, либо заменяет текст и клавиатуру

    return: Клавиатура с кнопками
            1) Тип рассылки 1
            N) Тип рассылки N
            N+1) отмена
    """
    keyboard = InlineKeyboardBuilder()

    for _, message_type in message_types.types.iterrows():
        call_data = callbacks.ApproveDeleteMessageByType(
            message_type_id=message_type['id'],
        )

        keyboard.row(types.InlineKeyboardButton(text=message_type['description'], callback_data=call_data.pack()))
    keyboard.row(types.InlineKeyboardButton(text='Отмена', callback_data=constants.CANCEL_CALLBACK))

    return keyboard.as_markup()


def get_approve_delete_messages_by_type_kb(message_type_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для типа рассылки, по которой можно удалить сообщения

    return: Клавиатура с кнопками
            1a) да
            1b) нет
            2) назад
    """
    keyboard = InlineKeyboardBuilder()
    call_data = callbacks.DeleteMessageByType(
        message_type_id=message_type_id,
    )
    keyboard.row(types.InlineKeyboardButton(text='Да', callback_data=call_data.pack()))
    keyboard.add(
        types.InlineKeyboardButton(
            text='Нет',
            callback_data=callback_prefixes.BACK_TO_DELETE_NEWSLETTER_MSG_MENU,
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data=callback_prefixes.BACK_TO_DELETE_NEWSLETTER_MSG_MENU,
        )
    )

    return keyboard.as_markup()
