"""
Вспомогательные функции для просмотра call report'ов
"""
from aiogram.types import Message

from configs import config
from handlers.call_reports.call_report_view.keyboards import get_keyboard_for_view_call_report, \
    get_keyboard_for_edit_call_report  # get_keyboard_for_edit_call_report, \
from handlers.call_reports.call_reports import CallReport
from handlers.call_reports.callbackdata import CRMenusEnum
from module.email_send import SmtpSend


async def send_to_mail(user_email, client, date, description) -> None:
    """
    Отправка по почте call report'ов

    :param user_email: Почта
    :param client: Имя клиента у call report'а
    :param date: Дата у call report'а
    :param description: Содержание call report'а
    """
    with SmtpSend(
            config.MAIL_RU_LOGIN,
            config.MAIL_RU_PASSWORD,
            config.mail_smpt_server,
            config.mail_smpt_port
    ) as SS:
        SS.send_msg(
            config.MAIL_RU_LOGIN,
            user_email,
            f'Протокол Встречи: {client} {date}',
            (
                f'Клиент: {client}\n'
                f'Дата: {date}\n'
                f'Запись встречи: {description}\n'
            ),
        )


async def call_report_view_answer(
        message: Message,
        report: CallReport,
        return_menu: CRMenusEnum,
        edit_message=True,
        custom_send_mail_button=False,
) -> None:
    """
    Основное меню просмотра call report'ов

    :param message: Сообщение
    :param report: Call report
    :param return_menu: Меню для возвращения, т.к. в данное меню можно перейти из нескольких мест
    :param edit_message: Параметр для указания нужно ли редактировать сообщение или отправить новое
    :param custom_send_mail_button: Параметр отвечающий за название кнопки отправки call report'а на почту
    """

    text = (
        'Протокол встречи:\n'
        f'Клиент: {report.client}\n'
        f'Дата: {report.date()}\n'
        f'Запись встречи: {report.description}\n'
    )
    keyboard = get_keyboard_for_view_call_report(report._id, return_menu, custom_send_mail_button).as_markup()
    if edit_message:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


async def call_report_edit_answer(
        message: Message,
        report: CallReport,
        return_menu: CRMenusEnum.main | CRMenusEnum.date_choice,
        edit_message=True,
) -> None:
    """
    Меню редактирования call report'ов

    :param message: Сообщение
    :param report: Call report
    :param return_menu: Меню для возвращения, т.к. в данное меню можно перейти из нескольких мест
    :param edit_message: Параметр для указания нужно ли редактировать сообщение или отправить новое
    """

    if edit_message:
        await message.edit_text(
            (
                'Протокол встречи:\n'
                f'Клиент: {report.client}\n'
                f'Дата: {report.date()}\n'
                f'Запись встречи: {report.description}\n'
            ),
            reply_markup=get_keyboard_for_edit_call_report(report._id, return_menu).as_markup(),
        )
    else:
        await message.answer(
            (
                'Протокол встречи:\n'
                f'Клиент: {report.client}\n'
                f'Дата: {report.date()}\n'
                f'Запись встречи: {report.description}\n'
            ),
            reply_markup=get_keyboard_for_edit_call_report(report._id, return_menu).as_markup(),
        )
