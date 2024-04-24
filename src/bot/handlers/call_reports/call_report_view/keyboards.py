"""
Набор функций для создания кнопок при просмотре call report'ов
"""
import copy

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from configs import config
from handlers.call_reports.callbackdata import CRMenusEnum, CRViewAndEdit, CRMainMenu

emoji = copy.deepcopy(config.dict_of_emoji)


def get_keyboard_for_view_call_report(
        report_id: int,
        return_menu: CRMenusEnum,
        custom_send_mail_button: bool = False
) -> InlineKeyboardBuilder:
    """
    Клавиатура появляющаяся при просмотре call report'ов

    :param report_id: айди в базе call report'а
    :param return_menu: меню для возвращения, т.к. в данное меню можно перейти из нескольких мест
    :param custom_send_mail_button: Параметр отвечающий за название кнопки отправки call report'а на почту
    """
    keyboard = InlineKeyboardBuilder()
    if custom_send_mail_button:
        send_mail_text = 'Протокол на почту отправлен'
    else:
        send_mail_text = 'Отправить на почту'

    keyboard.row(
        InlineKeyboardButton(
            text=send_mail_text,
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.send_to_mail,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='Редактировать',
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.edit_report,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    match return_menu:
        case CRMenusEnum.main:
            keyboard.row(
                InlineKeyboardButton(
                    text='В главное меню',
                    callback_data=CRMainMenu(
                        menu=CRMenusEnum.main,
                    ).pack()
                )
            )
        case CRMenusEnum.date_choice | CRMenusEnum.return_to_date_choice:
            keyboard.row(
                InlineKeyboardButton(
                    text='Назад',
                    callback_data=CRViewAndEdit(
                        menu=CRMenusEnum.return_to_date_choice,
                        report_id=report_id,
                    ).pack()
                )
            )
            keyboard.row(
                InlineKeyboardButton(
                    text='Завершить',
                    callback_data=CRMainMenu(
                        menu=CRMenusEnum.main,
                    ).pack()
                )
            )
        case _:
            raise Exception  # FIXME

    return keyboard


def get_keyboard_for_edit_call_report(report_id: int, return_menu: CRMenusEnum):
    """
    Клавиатура появляющаяся при редактировании call report'ов

    :param report_id: айди в базе call report'а
    :param return_menu: меню для возвращения, т.к. в данное меню можно перейти из нескольких мест
    """

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text='Изменить клиента',
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.edit_report_name,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='Изменить дату',
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.edit_report_date,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='Изменить описание',
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.edit_report_description,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='Назад',
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.report_view,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='Завершить',
            callback_data=CRMainMenu(
                menu=CRMenusEnum.main,
            ).pack()
        )
    )
    return keyboard
