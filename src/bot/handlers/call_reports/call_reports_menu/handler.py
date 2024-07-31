"""Handlers для выбора call report'ов"""
import copy

from aiogram import F, Router, types
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from configs import config
from db.api.client import client_db
from db.call_reports import get_all_dates_for_client_report, get_all_sorted_clients_for_user
from handlers.call_reports.call_reports import CallReport
from handlers.call_reports.callbackdata import CRChoiceReportView, CRCreateNew, CRMainMenu, CRMenusEnum, CRViewAndEdit
from handlers.clients import callback_data_factories

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
                text='Создать новую заметку',
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
            'Похоже у вас еще нет заметок',
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
            'Существующие заметки:',
            reply_markup=keyboard.as_markup(),
        )


@router.callback_query(CRChoiceReportView.filter(F.menu == CRMenusEnum.date_choice))
async def call_reports_handler_my_reports_date(
        callback_query: CallbackQuery,
        callback_data: CRChoiceReportView | callback_data_factories.ClientsMenuData,
) -> None:
    """
    Меню для просмотров дат call report'ов определенного клиента

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    sub_menu = None
    if isinstance(callback_data, callback_data_factories.ClientsMenuData):
        client_info = await client_db.get(callback_data.client_id)
        client_name = client_info['name']
        sub_menu = callback_data.pack()
        callback_data = CRChoiceReportView(
            menu=CRMenusEnum.date_choice,
            client=client_name,
            client_page=0,
            date_page=0,
            sub_menu=sub_menu,
        )
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
                    sub_menu=sub_menu,
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
                    sub_menu=sub_menu,
                ).pack()
            )
        )

    if callback_data.sub_menu is not None:
        cb_data = callback_data_factories.ClientsMenuData.unpack(callback_data.sub_menu)
        cb_data.menu = callback_data_factories.ClientsMenusEnum.client_menu
    else:
        cb_data = CRChoiceReportView(
            menu=CRMenusEnum.client_choice,
            client=callback_data.client,
            client_page=callback_data.client_page,
        )

    keyboard_footer.append(
        types.InlineKeyboardButton(
            text='Назад',
            callback_data=cb_data.pack(),
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
                    sub_menu=sub_menu,
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
        f'Заметка: "{callback_data.client}"',
        reply_markup=keyboard.as_markup(),
    )


@router.callback_query(CRViewAndEdit.filter(F.menu == CRMenusEnum.return_to_date_choice))
async def return_to_date_page(
        callback_query: CallbackQuery,
        callback_data: CRViewAndEdit,
        session: AsyncSession,
) -> None:
    """
    Функция для возврата в меню дат call report'ов определенного клиента

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param session: Сессия для взаимодействия с БД
    """
    report = CallReport(session)
    await report.setup(callback_data.report_id)
    client_page, date_page = await report.get_pages()

    await call_reports_handler_my_reports_date(
        callback_query,
        CRChoiceReportView(
            menu=CRMenusEnum.date_choice,
            client=report.client,
            client_page=client_page,
            date_page=date_page,
            sub_menu=callback_data.sub_menu,
        )
    )
