from enum import Enum

from aiogram.filters.callback_data import CallbackData

prefix = 'call_reports'


class CallReportsMenus(str, Enum):
    main = 'main'
    close = 'close'
    create_new = 'create_new'
    send_to_mail_from_state = 'to_mail_state'
    send_to_mail = 'send_to_mail'
    my_reports = 'my_reports'
    edit_report = 'edit_reports'
    edit_report_name = 'edit_name'
    edit_report_date = 'edit_date'
    edit_report_description = 'edit_dscr'


class CallReportsCallbackData(CallbackData, prefix=prefix):
    menu: CallReportsMenus = CallReportsMenus.my_reports
    client: str | None = None
    page: int = 0
    page_date: int = 0
    call_report_id: int = 0
