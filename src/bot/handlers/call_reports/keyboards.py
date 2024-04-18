import copy

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from configs import config
from handlers.call_reports.callbackdata import CallReportsCallbackData, CallReportsMenus

emoji = copy.deepcopy(config.dict_of_emoji)


def add_pagination_keyboard_client(
        keyboard: InlineKeyboardBuilder,
        active_prev_page: bool = False,
        active_next_page: bool = False,

):
    tmp_keyboard = []
    if active_prev_page:
        tmp_keyboard.append(InlineKeyboardButton())
    else:
        pass


def main_menu_keyboard() -> InlineKeyboardBuilder:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text='Создать новый протокол встречи',
            callback_data=CallReportsCallbackData(menu=CallReportsMenus.create_new).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='Посмотреть мои протоколы',
            callback_data=CallReportsCallbackData(menu=CallReportsMenus.my_reports).pack(),
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text='Закрыть',
            callback_data=CallReportsCallbackData(menu=CallReportsMenus.close).pack(),
        )
    )
    return keyboard


# def add_pagination(
#         keyboard: InlineKeyboardBuilder,
#         active_prev_page: bool = False,
#         active_next_page: bool = False,
#         other_params: dict = None) -> InlineKeyboardBuilder:
#     keys = []
#     if active_prev_page:
#         keys.append(
#             InlineKeyboardButton(
#                 text=f'{emoji["backward"]}',
#                 callback_data=CallReportsCallbackData(
#                     next_page=
#                 ).pack()
#             )
#         )

def get_keyboard_for_view_call_report(
        callback_data: CallReportsCallbackData | dict[str, CallReportsMenus | int | str]):
    if isinstance(callback_data, dict):
        callback_data = CallReportsCallbackData(**callback_data)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=f'Изменить клиента',
            callback_data=CallReportsCallbackData(
                menu=CallReportsMenus.edit_report_name,
                **callback_data.model_dump(include={'client', 'page', 'page_date', 'call_report_id'})
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=f'Изменить дату',
            callback_data=CallReportsCallbackData(
                menu=CallReportsMenus.edit_report_date,
                **callback_data.model_dump(include={'client', 'page', 'page_date', 'call_report_id'})
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=f'Изменить описание',
            callback_data=CallReportsCallbackData(
                menu=CallReportsMenus.edit_report_description,
                **callback_data.model_dump(include={'client', 'page', 'page_date', 'call_report_id'})
            ).pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=f'Назад',
            callback_data=CallReportsCallbackData(
                menu=CallReportsMenus.my_reports,
                **callback_data.model_dump(include={'client', 'page', 'page_date', 'call_report_id'})
            ).pack()
        )
    )
    return keyboard
