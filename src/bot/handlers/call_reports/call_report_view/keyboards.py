import copy

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from configs import config
from handlers.call_reports.callbackdata import CRMenusEnum, CRViewAndEdit, CRMainMenu

emoji = copy.deepcopy(config.dict_of_emoji)


def get_keyboard_for_view_call_report(report_id: int, return_menu: CRMenusEnum, custom_send_main_button):
    keyboard = InlineKeyboardBuilder()
    if custom_send_main_button:
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
            text=f'Редактировать',
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


def get_keyboard_for_edit_call_report(report_id, return_menu):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=f'Изменить клиента',
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.edit_report_name,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=f'Изменить дату',
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.edit_report_date,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=f'Изменить описание',
            callback_data=CRViewAndEdit(
                menu=CRMenusEnum.edit_report_description,
                report_id=report_id,
                return_menu=return_menu,
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=f'Назад',
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
