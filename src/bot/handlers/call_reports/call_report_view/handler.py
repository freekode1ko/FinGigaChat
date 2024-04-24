from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.call_reports.call_report_create.utils import validate_and_parse_date
from handlers.call_reports.call_report_view.utils import call_report_view_answer, send_to_mail, call_report_edit_answer
from handlers.call_reports.call_reports import CallReport
from handlers.call_reports.callbackdata import CRViewAndEdit, CRMenusEnum
from log.bot_logger import logger
from src.web_app.db.meeting import get_user_email_async

router = Router()


class CallReportsEditStates(StatesGroup):
    edit_clint_name = State()
    edit_date = State()
    edit_text_message = State()


@router.callback_query(CRViewAndEdit.filter(F.menu == CRMenusEnum.report_view))
async def show_report(
        callback_query: types.CallbackQuery,
        callback_data: CRViewAndEdit,
) -> None:
    report = CallReport()
    await report.setup(callback_data.report_id)

    await call_report_view_answer(callback_query.message, report, callback_data.return_menu)


@router.callback_query(CRViewAndEdit.filter(F.menu == CRMenusEnum.send_to_mail))
async def call_reports_handler_send_to_mail(
        callback_query: types.CallbackQuery,
        callback_data: CRViewAndEdit,
) -> None:
    """
    Обработка кнопок отправки на почту кол репорта

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Нажали на кнопку отправки на почту report для {callback_query.message.chat.id}')

    report = CallReport()
    await report.setup(callback_data.report_id)
    user_email = await get_user_email_async(user_id=report.user_id)

    try:
        logger.info(f'Call Report: Начало отправки на почту report для {callback_query.message.chat.id}')

        await send_to_mail(user_email, report.client, report.date(), report.description)

        await call_report_view_answer(
            callback_query.message,
            report,
            callback_data.return_menu,
            custom_send_main_button=True
        )
    except Exception as e:
        logger.error(
            f'Call Report: Письмо не отправлено на почту report для {callback_query.message.chat.id} из-за {e}')
    finally:
        logger.info(f'Call Report: Письмо успешно отправлено на почту report для {callback_query.message.chat.id}')


@router.callback_query(CRViewAndEdit.filter(F.menu == CRMenusEnum.edit_report))
async def edit_report(
        callback_query: types.CallbackQuery,
        callback_data: CRViewAndEdit,
) -> None:
    report = CallReport()
    await report.setup(callback_data.report_id)

    await call_report_edit_answer(callback_query.message, report, callback_data.return_menu)


@router.callback_query(CRViewAndEdit.filter(F.menu == CRMenusEnum.edit_report_name))
async def call_reports_edit_report_name(
        callback_query: types.CallbackQuery,
        callback_data: CRViewAndEdit,
        state: FSMContext,
) -> None:
    report = CallReport()
    await report.setup(callback_data.report_id)

    await state.set_state(CallReportsEditStates.edit_clint_name)
    await state.update_data(**callback_data.model_dump())
    await callback_query.message.edit_text(
        (
            f'Изменение имени клиента.\n\n'
            f'Предыдущее значение: {report.client}\n\n'
            f'Введите новое значение в чат!'
        ),
        reply_markup=None,
    )


@router.message(CallReportsEditStates.edit_clint_name)
async def call_reports_edit_name(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()

    report = CallReport()
    await report.setup(data['report_id'])
    await report.update_clint(message.text)

    await call_report_edit_answer(message, report, data['return_menu'], edit_message=False)


@router.callback_query(CRViewAndEdit.filter(F.menu == CRMenusEnum.edit_report_date))
async def call_reports_edit_report_name(
        callback_query: types.CallbackQuery,
        callback_data: CRViewAndEdit,
        state: FSMContext,
) -> None:
    report = CallReport()
    await report.setup(callback_data.report_id)

    await state.set_state(CallReportsEditStates.edit_date)
    await state.update_data(**callback_data.model_dump())
    await callback_query.message.edit_text(
        (
            f'Изменение даты.\n\n'
            f'Предыдущее значение: {report.date()}\n\n'
            f'Введите новое значение в чат!'
        ),
        reply_markup=None,
    )


@router.message(CallReportsEditStates.edit_date)
async def call_reports_edit_name(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    if date := validate_and_parse_date(message.text):
        report = CallReport()
        await report.setup(data['report_id'])
        await report.update_date(date)
        await call_report_edit_answer(message, report, data['return_menu'], edit_message=False)
    else:
        await message.answer(
            'Дата введена некорректно.\nУбедитесь, что вы используете формат ДД.ММ.ГГГГ и попробуйте еще раз:',
        )


@router.callback_query(CRViewAndEdit.filter(F.menu == CRMenusEnum.edit_report_description))
async def call_reports_edit_report_name(
        callback_query: types.CallbackQuery,
        callback_data: CRViewAndEdit,
        state: FSMContext,
) -> None:
    report = CallReport()
    await report.setup(callback_data.report_id)

    await state.set_state(CallReportsEditStates.edit_text_message)
    await state.update_data(**callback_data.model_dump())
    await callback_query.message.edit_text(
        (
            'Изменение описания.\n\n'
            f'Предыдущее значение: {report.description}\n\n'
            'Введите новое значение текстом в чат!'
        ),
        reply_markup=None,
    )


@router.message(CallReportsEditStates.edit_text_message)
async def call_reports_edit_name(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()

    report = CallReport()
    await report.setup(data['report_id'])
    await report.update_description(message.text)

    await call_report_edit_answer(message, report, data['return_menu'], edit_message=False)
