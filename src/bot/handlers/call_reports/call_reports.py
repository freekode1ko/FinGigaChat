"""Файл с главным меню и классом для работы с call report'ами"""
import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import insert, update

from configs import config
from db.call_reports import *
from handlers.call_reports.call_report_create.utils import validate_and_parse_date
from handlers.call_reports.callbackdata import CRCreateNew, CRMainMenu, CRMenusEnum
from log.bot_logger import logger
from utils.base import user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())


async def main_menu(message: Message, edit: bool = False) -> None:
    """
    Функция формирующая клавиатуру для главного меню

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param edit: Параметр для указания нужно ли редактировать сообщение или отправить новое
    """
    logger.info(f'Call Report: Страт call reports для {str(message.chat.id)}')

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text='Создать новый протокол встречи',
            callback_data=CRCreateNew(menu=CRMenusEnum.create_new).pack()
        )
    )
    # keyboard.row(
    #     InlineKeyboardButton(
    #         text='Посмотреть мои протоколы',
    #         callback_data=CRChoiceReportView(menu=CRMenusEnum.client_choice).pack(),
    #     )
    # )
    keyboard.row(
        InlineKeyboardButton(
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
async def call_reports_enter_command(message: Message, state: FSMContext, ) -> None:
    """
    Входная точка для создания или просмотра call report'ов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    await state.clear()
    if await user_in_whitelist(message.from_user.model_dump_json()):
        await main_menu(message)


@router.callback_query(CRMainMenu.filter(F.menu == CRMenusEnum.main))
async def call_reports_main_menu(
        callback_query: CallbackQuery,
        callback_data: CRMainMenu,
) -> None:
    """
    Входная точка для создания или просмотра call report'ов

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий дополнительную информацию
    """
    await main_menu(callback_query.message, True)


@router.callback_query(CRMainMenu.filter(F.menu == CRMenusEnum.close))
async def call_reports_close(
        callback_query: CallbackQuery,
        callback_data: CRMainMenu,
) -> None:
    """
    Функция для закрытия меню call report'ов

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий дополнительную информацию
    """
    await callback_query.message.edit_text(
        'Меню протоколов встреч закрыто.'
    )


class CallReport:
    """Класс для создания, изменения и получения call report'ов"""

    def __init__(self, session):
        self.session = session
        self.client = None
        self.report_date = None
        self.description = None
        self.user_id = None
        self._id = None

    async def setup(self, call_report_id, with_other_fields: bool = True) -> None:
        """
        Функция для получения всех данных о call report'е по айди

        :param call_report_id: Айди кол репорта
        :param with_other_fields: Параметр добавляющий возможность добавить только айди
        """
        self._id = call_report_id
        if with_other_fields:
            client_call_reports_dates = await self.session.execute(
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
        """
        Функция для создания call report'ов

        :param user_id: Айди пользователя
        :param client: Имя клиента
        :param report_date: Дата
        :param description: Описание call report'а
        """
        self.client = client
        self.user_id = user_id
        self.report_date = report_date
        self.description = description

        _id = await self.session.execute(
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
        await self.session.commit()

    def date(self) -> str:
        """
        Функция для корректного форматирования даты

        :return: Строка с датой
        """
        return self.report_date.strftime(config.BASE_DATE_FORMAT)

    async def update_clint(self, client: str) -> None:
        """
        Функция для обновления имени клиента

        :param client: Имя клиента
        """
        await self.session.execute(
            update(CallReports).values(client=client).where(
                CallReports.id == self._id
            )
        )
        await self.session.commit()
        self.client = client

    async def update_date(self, date: datetime.date | str) -> None:
        """
        Функция для обновления даты

        :param date: Дата
        """
        if isinstance(date, str):
            date = validate_and_parse_date(date)

        if date:
            await self.session.execute(
                update(CallReports).values(report_date=date).where(
                    CallReports.id == self._id
                )
            )
            await self.session.commit()
            self.report_date = date

    async def update_description(self, description: str) -> None:
        """
        Функция для обновления описания

        :param description: Описание
        """
        await self.session.execute(
            update(CallReports).values(description=description).where(
                CallReports.id == self._id
            )
        )
        await self.session.commit()
        self.description = description

    async def get_pages(self) -> None:
        """
        Функция для получения страниц call report'а для правильного возврата в меню выбора даты
        """
        dates = await get_all_dates_for_client_report(self.user_id, self.client)
        clients = await get_all_sorted_clients_for_user(self.user_id)

        return (clients.index(self.client) // config.PAGE_ELEMENTS_COUNT,
                dates.index((self._id, self.report_date)) // config.PAGE_ELEMENTS_COUNT)
