"""
Обработчик меню клиентов.

Позволяет получить различную информацию о клиенте:
- новости
- аналитика публичных рынков (для публичных клиентов)
- отраслевая аналитик
- продуктовые предложения
- цифровая справка
"""
import datetime
from pathlib import Path
from typing import Optional

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware

import utils.base
from constants import constants
from db import models
from db.api.client import client_db, get_research_type_id_by_name
from db.api.industry import get_industry_analytic_files
from db.api.product_group import product_group_db
from db.api.research_type import research_type_db
from db.api.user_client_subscription import user_client_subscription_db
from db.models import Article
from handlers import products
from handlers.analytics.analytics_sell_side.handler import get_researches_over_period
from handlers.clients import callback_data_factories
from handlers.clients import keyboards
from handlers.products import callbacks as products_callbacks
from keyboards.analytics.analytics_sell_side import callbacks as analytics_callbacks
from log.bot_logger import logger, user_logger
from module.article_process import FormatText
from module.fuzzy_search import FuzzyAlternativeNames
from utils.base import get_page_data_and_info, send_or_edit, send_pdf, user_in_whitelist


router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


class ChooseClient(StatesGroup):
    """Состояние для ввода имени клиента для более удобного поиска"""

    choosing_from_all_not_subscribed_clients = State()
    choosing_from_subscribed_clients = State()


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.end_menu
))
async def menu_end(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню клиенты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(text='Просмотр клиентов завершен')


async def main_menu(message: types.CallbackQuery | types.Message) -> None:
    """
    Формирует меню клиенты

    :param message: types.CallbackQuery | types.Message
    """
    keyboard = keyboards.get_menu_kb()
    msg_text = 'Клиенты'
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.main_menu
))
async def main_menu_callback(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Получение меню клиенты

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: содержит дополнительную информацию
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await main_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callback_data_factories.ClientsMenuData.__prefix__))
async def main_menu_command(message: types.Message) -> None:
    """
    Получение меню клиенты

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await main_menu(message)
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.clients_list
))
async def clients_list(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
        state: FSMContext,
) -> None:
    """
    Получение списка клиентов

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    msg_text = ''

    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = from_user.id

    subscribed = callback_data.subscribed
    page = callback_data.page
    clients = await client_db.get_all()
    client_subscriptions = await user_client_subscription_db.get_subscription_df(user_id)
    if subscribed:

        clients = clients[clients['id'].isin(client_subscriptions['id'])]
        await state.set_state(ChooseClient.choosing_from_subscribed_clients)
    else:
        clients = clients.iloc[0:0]
        await state.set_state(ChooseClient.choosing_from_all_not_subscribed_clients)

    page_data, page_info, max_pages = get_page_data_and_info(clients, page)
    keyboard = keyboards.get_clients_list_kb(page_data, page, max_pages, subscribed)

    if subscribed:
        msg_text = f'Выберите клиента из списка ваших подписок\n<b>{page_info}</b>\n\n'
    msg_text += 'Для поиска введите сообщение с именем клиента.'

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(ChooseClient.choosing_from_subscribed_clients)
@router.message(ChooseClient.choosing_from_all_not_subscribed_clients)
async def clients_subscriptions_list(
        message: types.Message,
        state: FSMContext,
) -> None:
    """
    Поиск по клиентам, на которые пользователь подписаны

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    subscribed = await state.get_state() == ChooseClient.choosing_from_subscribed_clients.state

    fuzzy_searcher = FuzzyAlternativeNames(logger=logger)
    clients_id = await fuzzy_searcher.find_subjects_id_by_name(message.text, subject_types=[models.ClientAlternative])
    clients = await client_db.get_by_ids(clients_id)
    client_subscriptions = await user_client_subscription_db.get_subscription_df(message.chat.id)

    if subscribed:
        clients = clients[clients['id'].isin(client_subscriptions['id'])]
    else:
        clients = clients[~clients['id'].isin(client_subscriptions['id'])]

    if len(clients) > 1:
        page_data, page_info, max_pages = get_page_data_and_info(clients)
        keyboard = keyboards.get_clients_list_kb(page_data, 0, max_pages, subscribed)
        msg_text = 'Выберите клиента из списка'
    elif len(clients) == 1:
        client_name = clients['name'].iloc[0]
        keyboard = keyboards.get_client_menu_kb(
            clients['id'].iloc[0],
            current_page=0,
            subscribed=subscribed,
            research_type_id=await get_research_type_id_by_name(client_name),
        )
        msg_text = f'Выберите раздел для получения данных по клиенту <b>{client_name}</b>'
    else:
        msg_text = 'Не нашелся, введите имя клиента по-другому'
        keyboard = None

    await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.client_menu
))
async def get_client_menu(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Меню разделов по клиенту

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client_id = callback_data.client_id
    client_info = await client_db.get(client_id)
    research_type_id = await get_research_type_id_by_name(client_info['name'])

    keyboard = keyboards.get_client_menu_kb(
        client_id,
        current_page=callback_data.page,
        subscribed=callback_data.subscribed,
        research_type_id=research_type_id,
    )
    msg_text = f'Выберите раздел для получения данных по клиенту <b>{client_info["name"].capitalize()}</b>'
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.client_news_menu
))
async def get_client_news_menu(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Меню получения новостей по клиенту

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client_id = callback_data.client_id
    client_info = await client_db.get(client_id)
    keyboard = keyboards.get_news_menu_kb(
        client_id,
        current_page=callback_data.page,
        subscribed=callback_data.subscribed,
    )
    msg_text = f'Какие новости вы хотите получить по клиенту <b>{client_info["name"].capitalize()}</b>'

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.analytic_indicators
))
async def get_client_analytic_indicators(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Меню аналитических показателей по клиенту, если есть research_type_id

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    callback_data.menu = callback_data_factories.ClientsMenusEnum.client_menu

    research_type_id = callback_data.research_type_id

    research_info = await research_type_db.get(research_type_id)

    msg_text = f'Какие данные вас интересуют по клиенту <b>{research_info.name}</b>?'
    keyboard = keyboards.client_analytical_indicators_kb(
        client_id=callback_data.client_id,
        current_page=callback_data.page,
        subscribed=callback_data.subscribed,
        research_type_id=research_type_id,
    )

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.industry_analytics
))
async def get_client_industry_analytics(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Получение файлов по отраслевой аналитике, к которой принадлежит клиент

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client_info = await client_db.get(callback_data.client_id)

    msg_text = (
        f'Отраслевая аналитика по клиенту <b>{client_info["name"].capitalize()}</b>\n'
    )

    files = await get_industry_analytic_files(industry_id=client_info['industry_id'])
    files = [p for f in files if (p := Path(f.file_path)).exists()]
    if not await send_pdf(callback_query, files, msg_text, protect_content=True):
        msg_text += '\nФункционал появится позднее'
        await callback_query.message.answer(msg_text, protect_content=True, parse_mode='HTML')

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.products
))
async def get_client_products_menu(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Получение продуктовых предложений по клиенту

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    # FIXME Узнать у Никиты, надо ли добавить остальные кнопки меню или пока нет
    client_info = await client_db.get(callback_data.client_id)
    keyboard = keyboards.get_products_menu_kb(
        callback_data.client_id,
        current_page=callback_data.page,
        subscribed=callback_data.subscribed,
    )

    msg_text = f'Продуктовые предложения по клиенту <b>{client_info["name"].capitalize()}</b>'
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.inavigator
))
async def get_client_inavigator(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Получение ссылки на inavigator клиента

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client_info = await client_db.get(callback_data.client_id)
    if client_info['navi_link']:
        msg_text = f'<a href="{str(client_info["navi_link"])}">Цифровая справка клиента: "{client_info["name"].capitalize()}"</a>'
    else:
        msg_text = f'Цифровая справка по клиенту "{client_info["name"].capitalize()}" отсутствует'

    await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.meetings_data
))
async def get_client_meetings_data(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Сформировать материалы для встречи

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client_info = await client_db.get(callback_data.client_id)

    msg_text = (
        f'Материалы для встречи по клиенту <b>{client_info["name"].capitalize()}</b>\n'
        f'Функциональность будет реализована позднее'
    )
    await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.call_reports
))
async def get_client_call_reports_menu(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Получение меню call reports клиента

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    from handlers.call_reports.call_reports_menu.handler import call_reports_handler_my_reports_date

    await call_reports_handler_my_reports_date(callback_query, callback_data)


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.top_news
))
async def get_client_top_news(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Получение топ новостей по клиенту

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    # FIXME Никита узнает у Саши С и скажет, что отправлять тут

    client_info = await client_db.get(callback_data.client_id)

    msg_text = (
        f'Топ новости по клиенту <b>{client_info["name"].capitalize()}</b>\n'
        f'Функциональность будет реализована позднее'
    )
    await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.select_period
))
async def get_client_select_period_menu(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
        select_period_menu: Optional[callback_data_factories.ClientsMenusEnum] = None,
        back_menu: Optional[callback_data_factories.ClientsMenusEnum] = None,
) -> None:
    """
    Меню выбора периода для выгрузки новостей по клиенту

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    :param select_period_menu: callback_data_factories.ClientsMenusEnum пункт меню, в который ведет выбор периода
    :param back_menu: callback_data_factories.ClientsMenusEnum пункт меню, в который ведет кнопка Назад
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client_info = await client_db.get(callback_data.client_id)
    select_period_menu = select_period_menu or callback_data_factories.ClientsMenusEnum.news_by_period
    back_menu = back_menu or callback_data_factories.ClientsMenusEnum.client_news_menu

    keyboard = keyboards.get_periods_kb(
        callback_data.client_id,
        current_page=callback_data.page,
        subscribed=callback_data.subscribed,
        research_type_id=callback_data.research_type_id,
        periods=constants.GET_NEWS_PERIODS,
        select_period_menu=select_period_menu,
        back_menu=back_menu,
    )
    msg_text = f'Выберите период для получения новостей по клиенту <b>{client_info["name"].capitalize()}</b>'
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.hot_offers
))
async def get_client_hot_offers(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Выдача файлов продуктовых предложений по клиенту

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    group = await product_group_db.get_by_latin_name('hot_offers')
    products_callback_data = products_callbacks.ProductsMenuData(
        menu=products_callbacks.ProductsMenusEnum.group_products,
        group_id=group.id,
        format_type=products_callbacks.FormatType.individual_messages,
    )
    callback_data.menu = callback_data_factories.ClientsMenusEnum.products
    await products.get_group_products(callback_query, products_callback_data, callback_data.pack())


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.news_by_period
))
async def get_client_news_by_period(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Получение новостей по клиенту за выбранный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client_id = callback_data.client_id
    days = callback_data.days_count
    client_info = await client_db.get(client_id)

    to_date = datetime.datetime.now()
    from_date = to_date - datetime.timedelta(days=days)

    msg_text = f'Новости по клиенту <b>{client_info["name"].capitalize()}</b> за {days} дней\n'
    articles = await client_db.get_articles_by_subject_ids(client_id, from_date, to_date, order_by=Article.date.desc())
    if not articles:
        msg_text += 'отсутствуют'
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    else:
        frmt_msg = f'<b>{client_info["name"].capitalize()}</b>'

        all_articles = '\n\n'.join(
            FormatText(
                title=article.title, date=article.date, link=article.link, text_sum=article.text_sum
            ).make_subject_text()
            for article, _ in articles
        )
        frmt_msg += f'\n\n{all_articles}'
        await callback_query.message.answer(msg_text, parse_mode='HTML')
        await utils.base.bot_send_msg(callback_query.bot, from_user.id, frmt_msg)

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.analytic_reports
))
async def analytic_reports(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Меню выбора периода для отправки отчетов за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит research_type_id
    """
    await get_client_select_period_menu(
        callback_query,
        callback_data,
        select_period_menu=callback_data_factories.ClientsMenusEnum.get_anal_reports,
        back_menu=callback_data_factories.ClientsMenusEnum.analytic_indicators,
    )


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.not_implemented
))
async def not_implemented(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Вывод сообщения, что функция еще не готова

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    msg_text = 'Функционал появится позднее'

    await callback_query.message.answer(msg_text, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.ClientsMenuData.filter(
    F.menu == callback_data_factories.ClientsMenusEnum.get_anal_reports
))
async def get_anal_reports(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.ClientsMenuData,
) -> None:
    """
    Отправка отчетов за указанный период

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит research_type_id
    """
    await get_researches_over_period(
        callback_query,
        analytics_callbacks.GetResearchesOverDays(
            research_type_id=callback_data.research_type_id,
            days_count=callback_data.days_count,
        ),
    )
