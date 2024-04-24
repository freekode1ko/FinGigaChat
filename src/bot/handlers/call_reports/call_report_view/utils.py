from aiogram import types

from configs import config
from handlers.call_reports.call_report_view.keyboards import get_keyboard_for_view_call_report, \
    get_keyboard_for_edit_call_report  # get_keyboard_for_edit_call_report, \
from handlers.call_reports.call_reports import CallReport
from handlers.call_reports.callbackdata import CRMenusEnum
from module.email_send import SmtpSend


async def send_to_mail(user_email, client, date, report):
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
                f'Запись встречи: {report}\n'
            ),
        )


async def call_report_view_answer(
        message: types.Message,
        report: CallReport,
        return_menu: CRMenusEnum,
        edit=True,
        custom_send_main_button=False,
) -> None:
    text = (
        'Протокол встречи:\n'
        f'Клиент: {report.client}\n'
        f'Дата: {report.date()}\n'
        f'Запись встречи: {report.description}\n'
    )
    keyboard = get_keyboard_for_view_call_report(report._id, return_menu, custom_send_main_button).as_markup()
    if edit:
        await message.edit_text(text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


async def call_report_edit_answer(
        message: types.Message,
        report: CallReport,
        return_menu: CRMenusEnum.main | CRMenusEnum.date_choice,
        edit_message=True,
) -> None:
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
