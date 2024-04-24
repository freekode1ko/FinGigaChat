from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData

prefix = 'CR'


class CRMenusEnum(IntEnum):
    main = auto()
    close = auto()

    create_new = auto()

    client_choice = auto()
    date_choice = auto()

    return_to_date_choice = auto()

    report_view = auto()

    edit_report = auto()
    edit_report_name = auto()
    edit_report_date = auto()
    edit_report_description = auto()

    send_to_mail = auto()


class CRMainMenu(CallbackData, prefix=prefix):
    menu: CRMenusEnum = CRMenusEnum.main


class CRCreateNew(CallbackData, prefix=prefix):
    menu: CRMenusEnum = CRMenusEnum.create_new


class CRChoiceReportView(CallbackData, prefix=prefix):
    menu: CRMenusEnum = CRMenusEnum.client_choice
    client: str | None = None
    client_page: int = 0
    date_page: int = 0


class CRViewAndEdit(CallbackData, prefix=prefix):
    menu: CRMenusEnum | None = None
    return_menu: CRMenusEnum = CRMenusEnum.main
    report_id: int | None = None
