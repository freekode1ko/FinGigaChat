"""
Handlers для создания call report'ов
"""
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.call_reports.call_report_create.utils import validate_and_parse_date, audio_to_text
from handlers.call_reports.call_report_view.utils import call_report_view_answer
from handlers.call_reports.call_reports import CallReport
from handlers.call_reports.callbackdata import CRCreateNew, CRMenusEnum
from log.bot_logger import logger

router = Router()


class CallReportsStates(StatesGroup):
    """
    Состояния при создании call report'ов
    enter_clint_name -> enter_date -> enter_text_message
    """
    enter_clint_name = State()
    enter_date = State()
    enter_description = State()


@router.callback_query(CRCreateNew.filter(F.menu == CRMenusEnum.create_new))
async def call_reports_handler_create_new(callback_query: CallbackQuery, state: FSMContext) -> None:
    """
    Обработка кнопки для создания нового кол репорта

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Нажали на конпу создания нового call report для {callback_query.message.chat.id}')
    await callback_query.message.answer(
        'Вы перешли в режим записи протокола встречи с клиентом следуйте инструкциям, чтобы завершить процесс.',
    )
    await callback_query.message.answer(
        'Пожалуйста, не включайте в отчет конфиденциальную информацию',
    )
    await callback_query.message.answer(
        'Введите, пожалуйста, Клиента, с кем проходила встреча:',
    )
    await state.set_state(CallReportsStates.enter_clint_name)


@router.message(CallReportsStates.enter_clint_name)
async def enter_clint_name(message: Message, state: FSMContext) -> None:
    """
    Обработка клиента, который ввел пользователь для создания кол репорта

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Сохранение клиента в call report для {message.chat.id}')
    if True:  # FIXME В дальнейшем будет браться из таблицы в БД
        await message.answer(
            'Укажите дату встречи в формате ДД.ММ.ГГГГ:',
        )
        await state.set_state(CallReportsStates.enter_date)
        await state.update_data(
            client=message.text,
        )


@router.message(CallReportsStates.enter_date)
async def enter_date(message: Message, state: FSMContext) -> None:
    """
    Обработка даты, который ввел пользователь для создания кол репорта

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Сохранение даты в call report для {message.chat.id}')
    if date := validate_and_parse_date(message.text):
        await message.answer(
            'Запишите основные моменты встречи(Голосом или текстом)',
        )
        await state.set_state(CallReportsStates.enter_description)
        await state.update_data(
            date=date,
        )
    else:
        await message.answer(
            'Дата введена некорректно.\nУбедитесь, что вы используете формат ДД.ММ.ГГГГ и попробуйте еще раз:',
        )
    logger.info(f'Call Report: Конец сохранения даты в call report для {message.chat.id}')


@router.message(CallReportsStates.enter_description, F.content_type.in_({'voice', 'text'}), )
async def enter_description(
        message: Message,
        state: FSMContext,
        session: AsyncSession) -> None:
    """
    Обработка текста/аудио, который ввел пользователь для создания кол репорта

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    logger.info(f'Call Report: Сохранения текста/аудио в call report для {message.chat.id}')

    if message.voice:
        result = await audio_to_text(message)
    else:
        result = message.text

    await state.update_data(
        text=result,
    )
    data = await state.get_data()

    report = CallReport(session)
    await report.create(
        user_id=message.from_user.id,
        client=data['client'],
        report_date=data['date'],
        description=data['text']
    )

    try:
        logger.info(f'Call Report: Сохранение call report для {message.chat.id}')

    except Exception as e:
        logger.error(f'Call Report: Сохранение call report не удалось для {message.chat.id} из-за {e}')
    finally:
        logger.info(f'Call Report: Успешное сохранение call report для {message.chat.id}')

    await call_report_view_answer(
        message,
        report,
        CRMenusEnum.main,
        edit_message=False
    )
    await state.clear()
    logger.info(f'Call Report: Конец сохранения текста/аудио в call report для {message.chat.id}')
