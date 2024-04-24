"""
Handlers для выбора call report'ов
"""
import copy

from aiogram import F, Router, types
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from configs import config
from db.call_reports import get_all_sorted_clients_for_user, get_all_dates_for_client_report
from handlers.call_reports.call_reports import CallReport
from handlers.call_reports.callbackdata import CRChoiceReportView, CRMenusEnum, CRMainMenu, CRCreateNew, CRViewAndEdit

router = Router()
emoji = copy.deepcopy(config.dict_of_emoji)


@router.callback_query(CRChoiceReportView.filter(F.menu == CRMenusEnum.client_choice))
async def call_reports_handler_my_reports(
        callback_query: CallbackQuery,
        callback_data: CRChoiceReportView,
) -> None:
    """
    Базовое меню просмотров всех клиентов у пользователя

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    clients = await get_all_sorted_clients_for_user(callback_query.message.chat.id)

    if not clients:
        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            types.InlineKeyboardButton(
                text='Создать новый протокол встречи',
                callback_data=CRCreateNew(menu=CRMenusEnum.create_new).pack()
            )
        )
        keyboard.row(
            types.InlineKeyboardButton(
                text='Назад',
                callback_data=CRMainMenu(menu=CRMenusEnum.main).pack()
            )
        )
        await callback_query.message.edit_text(
            'Похоже у вас еще нет протоколов встреч',
            reply_markup=keyboard.as_markup(),
        )
    else:
        keyboard = InlineKeyboardBuilder()
        for client in clients[
                      callback_data.client_page * config.PAGE_ELEMENTS_COUNT:
                      (callback_data.client_page + 1) * config.PAGE_ELEMENTS_COUNT
                      ]:
            keyboard.row(
                types.InlineKeyboardButton(
                    text=f'{client}',
                    callback_data=CRChoiceReportView(
                        menu=CRMenusEnum.date_choice,
                        client_page=callback_data.client_page,
                        client=client,
                    ).pack()
                )
            )
        keyboard_footer = []
        if callback_data.client_page > 0:
            keyboard_footer.append(
                types.InlineKeyboardButton(
                    text=f'{emoji["backward"]}',
                    callback_data=CRChoiceReportView(
                        menu=CRMenusEnum.client_choice,
                        client_page=callback_data.client_page - 1,
                    ).pack()
                )
            )
        keyboard_footer.append(
            types.InlineKeyboardButton(
                text='Назад',
                callback_data=CRMainMenu(menu=CRMenusEnum.main).pack()
            )
        )
        if len(clients) > (callback_data.client_page + 1) * config.PAGE_ELEMENTS_COUNT:
            keyboard_footer.append(
                types.InlineKeyboardButton(
                    text=f'{emoji["forward"]}',
                    callback_data=CRChoiceReportView(
                        menu=CRMenusEnum.client_choice,
                        client_page=callback_data.client_page + 1,
                    ).pack()
                )
            )
        keyboard.row(*keyboard_footer)
        await callback_query.message.edit_text(
            'Существующие протоколы встреч:',
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(CRChoiceReportView.filter(F.menu == CRMenusEnum.date_choice))
async def call_reports_handler_my_reports_date(
        callback_query: CallbackQuery,
        callback_data: CRChoiceReportView,
) -> None:
    """
    Меню для просмотров дат call report'ов определенного клиента

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    client_call_reports_dates = await get_all_dates_for_client_report(callback_query.message.chat.id,
                                                                      callback_data.client)

    keyboard = InlineKeyboardBuilder()
    for call_report_id, date in client_call_reports_dates[
                                callback_data.date_page * config.PAGE_ELEMENTS_COUNT:
                                (callback_data.date_page + 1) * config.PAGE_ELEMENTS_COUNT]:
        # Просмотр колл репорта по дате
        keyboard.row(
            types.InlineKeyboardButton(
                text=f'{date.strftime(config.BASE_DATE_FORMAT)}',
                callback_data=CRViewAndEdit(
                    menu=CRMenusEnum.report_view,
                    return_menu=CRMenusEnum.date_choice,
                    report_id=call_report_id,
                ).pack()
            )
        )

    keyboard_footer = []
    if callback_data.date_page > 0:
        keyboard_footer.append(
            types.InlineKeyboardButton(
                text=f'{emoji["backward"]}',
                callback_data=CRChoiceReportView(
                    menu=CRMenusEnum.date_choice,
                    client=callback_data.client,
                    client_page=callback_data.client_page,
                    date_page=callback_data.date_page - 1,
                ).pack()
            )
        )
    keyboard_footer.append(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data=CRChoiceReportView(
                menu=CRMenusEnum.client_choice,
                page=callback_data.client_page,
            ).pack()
        )
    )
    if len(client_call_reports_dates) > (callback_data.date_page + 1) * config.PAGE_ELEMENTS_COUNT:
        keyboard_footer.append(
            types.InlineKeyboardButton(
                text=f'{emoji["forward"]}',
                callback_data=CRChoiceReportView(
                    menu=CRMenusEnum.date_choice,
                    client=callback_data.client,
                    client_page=callback_data.client_page,
                    date_page=callback_data.date_page + 1,
                ).pack()
            )
        )
    keyboard.row(*keyboard_footer)
    keyboard.row(
        types.InlineKeyboardButton(
            text='Завершить',
            callback_data=CRMainMenu(
                menu=CRMenusEnum.main,
            ).pack()
        )
    )
    await callback_query.message.edit_text(
        f'Протокол встречи для клиента: "{callback_data.client}"',
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(CRViewAndEdit.filter(F.menu == CRMenusEnum.return_to_date_choice))
async def return_to_date_page(
        callback_query: CallbackQuery,
        callback_data: CRViewAndEdit,
) -> None:
    """
    Функция для возврата в меню дат call report'ов определенного клиента

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    report = CallReport()
    await report.setup(callback_data.report_id)
    client_page, date_page = await report.get_pages()

    await call_reports_handler_my_reports_date(
        callback_query,
        CRChoiceReportView(
            menu=CRMenusEnum.date_choice,
            client=report.client,
            client_page=client_page,
            date_page=date_page,
        )
    )
