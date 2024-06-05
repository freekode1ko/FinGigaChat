"""
Реализует интерфейс для работы с группой подписок на субъекты.

Позволяет просматирваться подписки, изменять подписки, удалять подписки.
"""
import copy
from typing import Protocol, Type

import pandas as pd
from aiogram import Router, types
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from configs import config
from constants import constants
from constants.subscriptions import const
from db import models
from db.api.industry import industry_db
from db.api.subject_interface import SubjectInterface
from db.api.subscriptions_interface import SubscriptionInterface
from db.api.user_research_subscription import user_research_subscription_db
from keyboards.subscriptions.news.news_keyboards import BaseKeyboard
from log.bot_logger import logger, user_logger
from module.fuzzy_search import FuzzyAlternativeNames
from utils.base import bot_send_msg, get_page_data_and_info, send_or_edit


emoji = copy.deepcopy(config.dict_of_emoji)


class CallbacksModule(Protocol):
    """Вызываемые модули"""

    @property
    def Menu(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def GetUserSubs(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def ChangeUserSubs(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def DeleteUserSub(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def PrepareDeleteAllSubs(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def DeleteAllSubs(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def SelectSubs(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def WriteSubs(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def ShowIndustry(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def WhatInThisIndustry(self) -> Type[CallbackData]: ...  # noqa:E704,D102

    @property
    def AddAllSubsByDomain(self) -> Type[CallbackData]: ...  # noqa:E704,D102


class NewsHandler:
    """Новостной хендлер"""

    callbacks: Type[CallbacksModule]

    def __init__(
            self,
            router: Router,
            subject_db: SubjectInterface,
            subscription_db: SubscriptionInterface,
            callbacks: Type[CallbacksModule],
            keyboards: BaseKeyboard,
            write_subscriptions_state: State,
            subject_names_to_find_nearest: list[models.Base],
            subject_name_nominative: str,
            subject_name_genitive: str,
            subject_name_accusative: str,
    ) -> None:
        """
        Инициализация обработчика подписок на новости

        :param router: aiogram.Router роутер
        :param subject_db: Интерфейс взаимодействия с клиентамы/сырьем/отраслями
        :param subscription_db: Интерфейс взаимодействия с подписками
        :param callbacks: Модуль фабрик колбэков
        :param keyboards: Модуль создания клавиатур
        :param subject_names_to_find_nearest: Список строк с названиями таблиц, в которых мы ищем максимально
                                              похожие слова (неточный поиск) ['client', 'commodity', 'industry']
        :param subject_name_nominative: название области подписок в именительном падеже (клиенты, сырьевые товары)
        :param subject_name_genitive: название области подписок в родительном падеже (клиентов, сырьевых товаров)
        :param subject_name_accusative: название области подписок в винительном падеже (клиентов, сырьевые товары)
        """
        self.router = router
        self.subject_db = subject_db
        self.subscription_db = subscription_db
        self.callbacks = callbacks
        self.keyboards = keyboards

        self.write_subscriptions_state = write_subscriptions_state
        self.subject_names_to_find_nearest = subject_names_to_find_nearest

        self.subject_inf = subject_name_nominative  # 'клиенты'   # сырьевые товары | отрасли
        self.subject_par = subject_name_genitive    # 'клиентов'  # сырьевых товаров | отраслей
        self.subject_vin = subject_name_accusative  # 'клиентов'  # сырьевые товары | отрасли

    def setup(self):
        """Сетап"""
        @self.router.callback_query(self.callbacks.ChangeUserSubs.filter())
        async def select_or_write(callback_query: types.CallbackQuery, state: FSMContext) -> None:
            keyboard = self.keyboards.change_subs_menu()
            await state.clear()
            await callback_query.message.edit_text('Как вы хотите заполнить подписки?', reply_markup=keyboard)

        @self.router.callback_query(self.callbacks.WriteSubs.filter())
        async def write_new_subscriptions_callback(
                callback_query: types.CallbackQuery,
                callback_data: CallbacksModule.WriteSubs,
                state: FSMContext,
        ) -> None:
            """
            Формирует ответное сообщение для добавления подписок

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: Доп инфа
            :param state: Состояние FSM
            """
            user_msg = callback_data.pack()
            from_user = callback_query.from_user
            full_name = f"{from_user.first_name} {from_user.last_name or ''}"
            chat_id = from_user.id

            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

            await state.set_state(self.write_subscriptions_state)
            keyboard = self.keyboards.show_industry_kb()
            await callback_query.message.edit_text(
                f'Сформируйте полный список интересующих {self.subject_par} '
                f'для подписки на пассивную отправку новостей по ним.\n'
                f'Перечислите их в одном следующем сообщении каждую с новой строки.\n'
                f'\nНапример:\nгаз\nгазпром\nнефть\nзолото\nбалтика\n\n'
                f'Вы также можете воспользоваться готовыми подборками клиентов и commodities, '
                f'которые отсортированы по отраслям. Скопируйте готовую подборку, исключите '
                f'лишние наименования или добавьте дополнительные.\n',
                reply_markup=keyboard,
            )

        @self.router.callback_query(self.callbacks.AddAllSubsByDomain.filter())
        async def add_all_subs(callback_query: types.CallbackQuery, callback_data: CallbacksModule.AddAllSubsByDomain) -> None:
            """
            Подписывает пользователя на все подписки из области

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: Содержит информацию о выбранной области
            """
            user_msg = callback_data.pack()
            from_user = callback_query.from_user
            full_name = f"{from_user.first_name} {from_user.last_name or ''}"
            user_id = from_user.id

            user_logger.info(f'*{user_id}* {full_name} - {user_msg}')

            user_subscription_df = await self.subscription_db.get_subscription_df(user_id)
            subject_df = await self.subject_db.get_all()

            elements_to_add = subject_df[~subject_df['id'].isin(user_subscription_df['id'])]

            if not elements_to_add.empty:
                await self.subscription_db.add_subscriptions(user_id, elements_to_add)
                await user_research_subscription_db.subscribe_on_news_source_with_same_name(
                    user_id, self.subscription_db.subject_table, elements_to_add['id'].tolist()
                )
                new_subs = ', '.join(elements_to_add['name'])

                msg_text = (
                    f'{new_subs} - добавлены к вашим подпискам\n'
                )
            else:
                msg_text = f'Вы уже подписаны на все {self.subject_par}\nВыберите другой раздел'

            await callback_query.message.answer(msg_text)

        @self.router.callback_query(self.callbacks.SelectSubs.filter())
        async def scroller(callback_query: types.CallbackQuery, callback_data: CallbacksModule.SelectSubs) -> None:
            """
            Меню с пагинацией для добавления подписок

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: номер страницы, id субъекта, на которого пользователь подписывается или отписывается
            """
            chat_id = callback_query.message.chat.id
            user_msg = callback_data.pack()
            from_user = callback_query.from_user
            full_name = f"{from_user.first_name} {from_user.last_name or ''}"
            user_id = callback_query.from_user.id

            title = f'Подборка {self.subject_par}'

            page = callback_data.page
            subject_id = callback_data.subject_id
            need_add = callback_data.need_add

            if subject_id:
                if need_add:
                    await self.subscription_db.add_subscription(user_id, subject_id)
                    await user_research_subscription_db.subscribe_on_news_source_with_same_name(
                        user_id, self.subscription_db.subject_table, subject_id
                    )
                else:
                    await self.subscription_db.delete_subscription(user_id, subject_id)

            subject_df = await self.subscription_db.get_subject_df(user_id)
            page_data, page_info, max_pages = get_page_data_and_info(subject_df, page)
            msg_text = (
                f'{title}\n<b>{page_info}</b>\n\n'
                f'Для добавления/удаления подписки нажмите на {constants.UNSELECTED}/{constants.SELECTED} соответственно'
            )
            keyboard = self.keyboards.get_subjects_kb(page_data, page, max_pages)

            await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

        @self.router.callback_query(self.callbacks.ShowIndustry.filter())
        async def showmeindustry(
                callback_query: types.CallbackQuery,
                callback_data: CallbacksModule.ShowIndustry,
        ) -> None:
            """
            Сообщение с кнопками для получения готовых сборок подписок по отраслям

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: Действие пользователя
            """
            from_user = callback_query.from_user
            chat_id = from_user.id
            user_logger.info(f'Пользователь *{chat_id}* решил воспользоваться готовыми сборками подписок')

            keyboard = InlineKeyboardBuilder()
            industries = await industry_db.get_all()
            subjects = await self.subject_db.get_all()
            industries = industries[industries['id'].isin(subjects['industry_id'])]

            for _, industry in industries.iterrows():
                keyboard.row(
                    types.InlineKeyboardButton(
                        text=industry['name'].capitalize(),
                        callback_data=self.callbacks.WhatInThisIndustry(industry_id=industry['id']).pack()),
                )
            await callback_query.message.answer(
                f'По какой отрасли вы бы хотели получить список {self.subject_par}?', reply_markup=keyboard.as_markup()
            )

        @self.router.callback_query(self.write_subscriptions_state, self.callbacks.WhatInThisIndustry.filter())
        async def whatinthisindustry(
                callback_query: types.CallbackQuery,
                callback_data: CallbacksModule.WhatInThisIndustry,
        ) -> None:
            """
            Отображение связанных с отраслью объектов (клиентов или сырья)

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: Содержит id отрасли
            """
            from_user = callback_query.from_user
            chat_id, user_first_name = from_user.id, from_user.first_name

            industry_id = callback_data.industry_id
            ref_book = await industry_db.get(industry_id)
            ref_book = ref_book['name']

            user_logger.info(f'Пользователь *{chat_id}* {user_first_name} смотрит список по {ref_book}')
            objects = await self.subject_db.get_by_industry_id(industry_id)
            all_objects = objects['name'].tolist()

            if all_objects:
                await bot_send_msg(
                    callback_query.message.bot,
                    chat_id,
                    '\n'.join([name.title() for name in all_objects]),
                    delimiter='\n',
                    prefix=constants.handbook_prefix.format(ref_book.upper()),
                )
                await callback_query.message.answer(
                    text='Вы можете скопировать список выше, отредактировать, если это необходимо и '
                    'отправить в бота следующем сообщением, чтобы список сохранился',
                )
            else:
                await callback_query.message.answer(
                    text=f'На данный момент в отрасли "{ref_book.upper()}" отсутствуют {self.subject_inf}'
                )

        @self.router.message(self.write_subscriptions_state)
        async def set_user_subscriptions(message: types.Message, state: FSMContext) -> None:
            """
            Обработка сообщения от пользователя и запись известных объектов новостей в подписки

            :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param state: конечный автомат о состоянии
            """
            chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}: настройка пользовательских подписок')
            message_text = user_msg
            quotes = ['\"', '«', '»']

            user_id = message.from_user.id

            user_subscription_df = await self.subscription_db.get_subscription_df(user_id)
            subject_other_name_df = await self.subject_db.get_other_names()

            for quote in quotes:
                message_text = message_text.replace(quote, '')

            user_request = [i.strip().lower() for i in message_text.split('\n')]
            subscriptions = subject_other_name_df[subject_other_name_df['other_name'].isin(user_request)]

            continue_keyboard = InlineKeyboardBuilder()
            continue_keyboard.add(types.InlineKeyboardButton(text='Завершить', callback_data=const.END_WRITE_SUBS))
            continue_keyboard = continue_keyboard.as_markup()
            continue_msg = '\n\nЕсли хотите завершить формирование подписок, то нажмите кнопку "Завершить"'

            new_subs = subscriptions[~subscriptions['id'].isin(user_subscription_df['id'])].drop_duplicates(subset='id')
            if len(subscriptions) < len(user_request):
                list_of_unknown = list(set(user_request) - set(subscriptions['other_name']))
                fuzzy_searcher = FuzzyAlternativeNames(logger=logger)
                near_to_list_of_unknown = '\n'.join(
                    await fuzzy_searcher.find_nearest_to_subjects_list(list_of_unknown, self.subject_names_to_find_nearest)
                )
                user_logger.info(f'*{user_id}* Пользователь запросил неизвестные новостные ' f'объекты на подписку: '
                                 f'{list_of_unknown}')
                reply_msg = f'{", ".join(list_of_unknown)} - Эти объекты новостей нам неизвестны'
                reply_msg += f'\n\nВозможно, вы имели в виду:\n{near_to_list_of_unknown}'
                # Если нет корректных названий, то новых подписок не добавляем и предлагаем пользователю
                # продолжить формирование
                # Иначе предлагаем продолжить в сообщении об успешном добавлении новых подписок
                keyboard = None
                if len(new_subs) == 0:
                    keyboard = continue_keyboard
                    reply_msg += continue_msg
                await message.reply(reply_msg, reply_markup=keyboard)

            # Если есть новые подписки, которые можем добавить
            if not new_subs.empty:
                await self.subscription_db.add_subscriptions(user_id, new_subs)
                await user_research_subscription_db.subscribe_on_news_source_with_same_name(
                    user_id, self.subscription_db.subject_table, new_subs['id'].tolist()
                )

                new_subs_str = ', '.join(new_subs['name']).title()
                user_logger.info(f'*{user_id}* Пользователь подписался на : {new_subs_str}')

                keyboard = continue_keyboard
                user_subs_str = '\n'.join(pd.concat([user_subscription_df['name'], new_subs['name']]))
                msg_txt = f'Ваш список подписок:\n\n{user_subs_str}'

                if len(msg_txt) + len(continue_msg) > 4096:
                    msg_txt = 'Ваши подписки были сохранены'

                msg_txt += continue_msg

                await message.reply(msg_txt, reply_markup=keyboard)

        @self.router.callback_query(self.callbacks.GetUserSubs.filter())
        async def get_user_subscriptions_callback(
                callback_query: types.CallbackQuery,
                callback_data: CallbacksModule.GetUserSubs,
        ) -> None:
            """
            Получение сообщением информации о своих подписках

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: Объект, содержащий в себе инфу о текущей странице
            """
            chat_id = callback_query.message.chat.id
            user_msg = callback_data.pack()
            from_user = callback_query.from_user
            full_name = f"{from_user.first_name} {from_user.last_name or ''}"
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

            title = f'Ваши подписки на {self.subject_vin}'

            user_id = callback_query.from_user.id
            page = callback_data.page

            user_subscription_df = await self.subscription_db.get_subscription_df(user_id)

            page_data, page_info, max_pages = get_page_data_and_info(user_subscription_df, page)
            keyboard = self.keyboards.get_watch_user_subscription_kb(page_data, page, max_pages)
            msg_txt = (
                f'{title}\n<b>{page_info}</b>\n\n'
                'Выберите подписку для получения новостей\n\n'
            )

            await callback_query.message.edit_text(msg_txt, reply_markup=keyboard, parse_mode='HTML')

        @self.router.callback_query(self.callbacks.DeleteUserSub.filter())
        async def delete_subscriptions(
                callback_query: types.CallbackQuery,
                callback_data: CallbacksModule.DeleteUserSub,
        ) -> None:
            """
            Получение сообщением информации о своих подписках для их удаления

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: номер страницы для отображения, subject_id для удаления подписки
            """
            chat_id = callback_query.message.chat.id
            user_msg = callback_data.pack()
            from_user = callback_query.from_user
            full_name = f"{from_user.first_name} {from_user.last_name or ''}"
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

            title = f'Ваши подписки на {self.subject_vin}'

            user_id = callback_query.from_user.id
            page = callback_data.page
            subject_id = callback_data.subject_id

            if subject_id:
                await self.subscription_db.delete_subscription(user_id, subject_id)

            user_subscription_df = await self.subscription_db.get_subscription_df(user_id)

            page_data, page_info, max_pages = get_page_data_and_info(user_subscription_df, page)
            keyboard = self.keyboards.get_delete_user_subscription_kb(page_data, page, max_pages)
            msg_txt = (
                f'{title}\n<b>{page_info}</b>\n\n'
                'Выберите подписку для удаления\n\n'
            )

            await callback_query.message.edit_text(msg_txt, reply_markup=keyboard, parse_mode='HTML')

        @self.router.callback_query(self.callbacks.DeleteAllSubs.filter())
        async def delete_all_subscriptions(
                callback_query: types.CallbackQuery,
                callback_data: CallbacksModule.DeleteAllSubs,
        ) -> None:
            """
            Получение сообщением информации о своих подписках для их удаления

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: Объект, содержащий в себе доп информацию
            """
            chat_id = callback_query.message.chat.id
            user_msg = callback_data.pack()
            from_user = callback_query.from_user
            full_name = f"{from_user.first_name} {from_user.last_name or ''}"
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
            user_id = from_user.id  # Get user_ID from message
            await self.subscription_db.delete_all(user_id)

            msg_txt = 'Подписки удалены'
            keyboard = self.keyboards.get_back_to_subscriptions_menu_kb()
            await callback_query.message.edit_text(text=msg_txt, reply_markup=keyboard)

        @self.router.callback_query(self.callbacks.PrepareDeleteAllSubs.filter())
        async def prepare_delete_all_subscriptions(
                callback_query: types.CallbackQuery,
                callback_data: CallbacksModule.PrepareDeleteAllSubs,
        ) -> None:
            """
            Подтвреждение действия

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: Объект, содержащий в себе доп информацию
            """
            chat_id = callback_query.message.chat.id
            user_msg = callback_data.pack()
            from_user = callback_query.from_user
            full_name = f"{from_user.first_name} {from_user.last_name or ''}"
            user_id = callback_query.from_user.id

            user_subs_df = await self.subscription_db.get_subscription_df(user_id=user_id)

            if user_subs_df.empty:
                msg_text = 'У вас отсутствуют подписки'
                keyboard = self.keyboards.get_back_to_subscriptions_menu_kb()
            else:
                msg_text = 'Вы уверены, что хотите удалить все подписки?'
                keyboard = self.keyboards.get_prepare_subs_delete_all_kb()

            await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

        @self.router.callback_query(self.callbacks.Menu.filter())
        async def subject_subscriptions_menu_callback(
                callback_query: types.CallbackQuery,
                callback_data: CallbacksModule.Menu,
        ) -> None:
            """
            Получение меню для взаимодействия с подписками

            :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
            :param callback_data: Объект, содержащий в себе доп информацию
            """
            chat_id = callback_query.message.chat.id
            user_msg = callback_data.pack()
            from_user = callback_query.from_user
            full_name = f"{from_user.first_name} {from_user.last_name or ''}"

            keyboard = self.keyboards.get_subscriptions_menu_kb()
            msg_text = f'Меню управления подписками на {self.subject_vin}\n'
            await send_or_edit(callback_query, msg_text, keyboard)
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
