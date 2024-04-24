import datetime

from aiogram import Router, F
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import update, insert

from configs import config
from db.call_reports import *
from handlers.call_reports.call_report_create.utils import validate_and_parse_date
from handlers.call_reports.callbackdata import CRMainMenu, CRCreateNew, CRChoiceReportView, CRMenusEnum
from log.bot_logger import logger
from utils.base import user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())


async def main_menu(message: types.Message, edit: bool = False) -> None:
    logger.info(f'Call Report: Страт call reports для {str(message.chat.id)}')

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        types.InlineKeyboardButton(
            text='Создать новый протокол встречи',
            callback_data=CRCreateNew(menu=CRMenusEnum.create_new).pack()
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Посмотреть мои протоколы',
            callback_data=CRChoiceReportView(menu=CRMenusEnum.client_choice).pack(),
        )
    )
    keyboard.row(
        types.InlineKeyboardButton(
            text='Закрыть',
            callback_data=CRMainMenu(menu=CRMenusEnum.close).pack(),
        )
    )

    if edit:
        await message.edit_text(
            'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?',
            reply_markup=keyboard.as_markup(),
        )
    else:
        await message.answer(
            'Вы вызвали функцию работы с протоколами встреч, что вы хотите сделать?',
            reply_markup=keyboard.as_markup(),
        )


@router.message(Command('call_reports'))
async def call_reports_enter_command(message: types.Message, state: FSMContext, ) -> None:
    """
    Входная точка для создания или просмотра кол репортов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    await state.clear()
    if await user_in_whitelist(message.from_user.model_dump_json()):
        await main_menu(message)


@router.callback_query(CRMainMenu.filter(F.menu == CRMenusEnum.main))
async def call_reports_main_menu(
        callback_query: types.CallbackQuery,
        callback_data: CRMainMenu,
) -> None:
    """
    Входная точка для создания или просмотра кол репортов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    await main_menu(callback_query.message, True)


@router.callback_query(CRMainMenu.filter(F.menu == CRMenusEnum.close))
async def call_reports_close(
        callback_query: types.CallbackQuery,
        callback_data: CRMainMenu,
) -> None:
    """
    Входная точка для создания или просмотра кол репортов

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: # FIXME
    """
    await callback_query.message.edit_text(
        "Меню протоколов встреч закрыто."
    )


class CallReport:
    def __init__(self):
        self.client = None
        self.report_date = None
        self.description = None
        self.user_id = None
        self._id = None

    async def setup(self, call_report_id, with_other_fields: bool = True):
        self._id = call_report_id
        if with_other_fields:
            async with async_session() as session:
                client_call_reports_dates = await session.execute(
                    select(
                        CallReports.client,
                        CallReports.report_date,
                        CallReports.description,
                        CallReports.user_id
                    )
                    .filter(
                        CallReports.id == self._id,
                    )
                )
                self.client, self.report_date, self.description, self.user_id = client_call_reports_dates.fetchone()

    async def create(self, user_id: str, client: int, report_date: datetime.date, description: str) -> None:
        self.client = client
        self.user_id = user_id
        self.report_date = report_date
        self.description = description

        async with async_session() as session:
            _id = await session.execute(
                insert(CallReports)
                .values(
                    user_id=user_id,
                    client=client,
                    report_date=report_date,
                    description=description
                )
                .returning(CallReports.id)
            )
            self._id = _id.first()[0]
            await session.commit()

    def date(self):
        return self.report_date.strftime(config.BASE_DATE_FORMAT)

    async def update_clint(self, client: str):
        async with async_session() as session:
            await session.execute(
                update(CallReports).values(client=client).where(
                    CallReports.id == self._id
                )
            )
            await session.commit()
        self.client = client

    async def update_date(self, date: datetime.date | str) -> None:
        if isinstance(date, str):
            date = validate_and_parse_date(date)

        if date:
            async with async_session() as session:
                await session.execute(
                    update(CallReports).values(report_date=date).where(
                        CallReports.id == self._id
                    )
                )
                await session.commit()
            self.report_date = date

    async def update_description(self, description: str) -> None:
        async with async_session() as session:
            await session.execute(
                update(CallReports).values(description=description).where(
                    CallReports.id == self._id
                )
            )
            await session.commit()
        self.description = description

    async def get_pages(self) -> None:
        dates = await get_all_dates_for_client_report(self.user_id, self.client)
        clients = await get_all_sorted_clients_for_user(self.user_id)

        return (clients.index(self.client) // config.PAGE_ELEMENTS_COUNT,
                dates.index((self._id, self.report_date)) // config.PAGE_ELEMENTS_COUNT)
