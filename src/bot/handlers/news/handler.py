"""
Обработчик для меню новостей.

Позволяет получать новости по тг каналам, отраслям, клиентам и сырьевым товарам.
"""
import asyncio
import datetime
from itertools import groupby
from typing import Union

import pandas as pd
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware

from constants import constants
from db import models
from db.api import industry
from db.api.subject_interface import SubjectInterface
from db.api.telegram_group import telegram_group_db
from db.api.telegram_section import telegram_section_db
from db.api.user_telegram_subscription import user_telegram_subscription_db
from handlers.news import callback_data_factories, keyboards, utils
from log.bot_logger import logger, user_logger
from module.article_process import ArticleProcess, FormatText
from module.fuzzy_search import FuzzyAlternativeNames
from utils.base import bot_send_msg, get_page_data_and_info, send_full_copy_of_message, send_or_edit, user_in_whitelist

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


STATE_DATA_NEWS_GETTER = 'news_getter'
STATE_DATA_SELECTED_SUBJECTS = 'selected'


class ChooseSubject(StatesGroup):
    """Состояние для ввода имени субъекта для более удобного поиска"""

    choosing_from_all_not_subscribed = State()
    choosing_from_subscribed = State()


@router.callback_query(callback_data_factories.NewsMenuData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.end_menu
))
async def menu_end(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню новости

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(text='Просмотр новостей завершен')


async def main_menu(message: types.CallbackQuery | types.Message, state: FSMContext) -> None:
    """
    Формирует меню новости

    :param message: types.CallbackQuery | types.Message
    :param state:   Объект, который хранит состояние FSM для пользователя
    """
    tg_groups = await telegram_group_db.get_all()
    keyboard = keyboards.get_menu_kb(tg_groups)
    msg_text = 'Новости'
    await state.set_data({})
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(callback_data_factories.NewsMenuData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.main_menu
))
@router.callback_query(callback_data_factories.TelegramGroupData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.main_menu
))
@router.callback_query(callback_data_factories.SubjectData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.main_menu
))
async def main_menu_callback(
        callback_query: types.CallbackQuery,
        callback_data: Union[callback_data_factories.NewsMenuData,
                             callback_data_factories.TelegramGroupData,
                             callback_data_factories.SubjectData],
        state: FSMContext,
) -> None:
    """
    Получение меню новости

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   содержит дополнительную информацию
    :param state:           Объект, который хранит состояние FSM для пользователя
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await main_menu(callback_query, state)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callback_data_factories.NewsMenuData.__prefix__))
async def main_menu_command(message: types.Message, state: FSMContext) -> None:
    """
    Получение меню новости

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state:   Объект, который хранит состояние FSM для пользователя
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await main_menu(message, state)
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.TelegramGroupData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.choose_telegram_subjects
))
async def choose_news_subjects(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.TelegramGroupData,
) -> None:
    """
    Отображает все тг каналы, если is_show_all_channels, либо отображает тг разделы.

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    group_id = callback_data.telegram_group_id
    telegram_group_info = await telegram_group_db.get(group_id)

    if telegram_group_info.is_show_all_channels:
        callback_data.back_menu = callback_data_factories.NewsMenusEnum.main_menu
        await __show_telegram_channels_by_group(callback_query, callback_data, telegram_group_info)
    else:
        await __show_telegram_sections_by_group(callback_query, callback_data, telegram_group_info)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def __show_telegram_channels_by_group(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.TelegramGroupData,
        telegram_group_info: models.TelegramGroup,
) -> None:
    """
    Формирует список тг каналов определенной группы (bot_telegram_group)

    :param callback_query:      Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:       Содержит информацию о текущем меню
    :param telegram_group_info: Объект телеграмм группы
    """
    selected_ids = utils.get_selected_ids_from_callback_data(callback_data)
    utils.update_selected_ids(selected_ids, callback_data.telegram_channel_id)
    callback_data.subject_ids = utils.wrap_selected_ids(selected_ids)

    telegram_channels = await user_telegram_subscription_db.get_subject_df_by_group_id(
        user_id=callback_query.from_user.id,
        group_id=telegram_group_info.id,
    )
    telegram_channels['is_subscribed'] = telegram_channels['id'].apply(lambda x: x in selected_ids)

    msg_text = (
        f'{telegram_group_info.name}\n\n'
        f'Выберите телеграм каналы, по которым хотите получить новости'
    )
    keyboard = keyboards.get_select_telegram_channels_kb(telegram_channels, callback_data)
    await send_or_edit(callback_query, msg_text, keyboard)


async def __show_telegram_sections_by_group(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.TelegramGroupData,
        telegram_group_info: models.TelegramGroup,
) -> None:
    """
    Формирует список тг разделов определенной группы (bot_telegram_group)

    :param callback_query:      Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:       Содержит информацию о текущем меню
    :param telegram_group_info: Объект телеграмм группы
    """
    telegram_sections = await telegram_section_db.get_by_group_id(group_id=telegram_group_info.id, only_with_channels=False)
    msg_text = 'Выберите отрасль для получения новостей'
    keyboard = keyboards.get_sections_menu_kb(telegram_sections, callback_data.telegram_group_id)
    await send_or_edit(callback_query, msg_text, keyboard)


@router.callback_query(callback_data_factories.TelegramGroupData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.choose_source_group,
))
async def choose_source_group(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.TelegramGroupData,
) -> None:
    """
    Формирует список тг каналов определенного раздела (bot_telegram_section)

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    section = await telegram_section_db.get(callback_data.telegram_section_id)

    keyboard = keyboards.get_choose_source_kb(callback_data)
    msg_text = f'Выберите откуда вы хотите получить новости по отрасли <b>{section.name}</b>'
    await send_or_edit(callback_query, msg_text, keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.TelegramGroupData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.telegram_channels_by_section,
))
async def telegram_channels_by_section(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.TelegramGroupData,
) -> None:
    """
    Формирует список тг каналов определенного раздела (bot_telegram_section)

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Содержит информацию о текущем меню
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    selected_ids = utils.get_selected_ids_from_callback_data(callback_data)
    utils.update_selected_ids(selected_ids, callback_data.telegram_channel_id)
    callback_data.subject_ids = utils.wrap_selected_ids(selected_ids)

    telegram_section_info = await telegram_section_db.get(callback_data.telegram_section_id)

    telegram_channels = await user_telegram_subscription_db.get_subject_df_by_section_id(
        user_id=callback_query.from_user.id,
        section_id=telegram_section_info.id,
    )
    telegram_channels['is_subscribed'] = telegram_channels['id'].apply(lambda x: x in selected_ids)

    callback_data.back_menu = callback_data_factories.NewsMenusEnum.choose_source_group
    keyboard = keyboards.get_select_telegram_channels_kb(telegram_channels, callback_data)
    msg_text = (
        f'Телеграм-каналы по отрасли "{telegram_section_info.name}"\n\n'
        f'Выберите телеграм каналы, по которым хотите получить новости'
    )
    await send_or_edit(callback_query, msg_text, keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.SubjectData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.choose_subs_or_unsubs
))
async def choose_subs_or_unsubs(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.SubjectData,
) -> None:
    """
    Меню разделения субъектов на тех, кто в подписках пользователя, и тех, кто нет.

    Позволяет пользователю быстрее найти нужный субъект для получения новостей.

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   Информация о выбранной группе субъектов (клиенты или сырье)
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    keyboard = keyboards.get_choose_subs_or_unsubs_kb(callback_data.subject)
    msg_text = callback_data.subject.title
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.SubjectData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.subjects_list
))
async def subjects_list(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.SubjectData,
        state: FSMContext,
) -> None:
    """
    Получение списка клиентов/сырья.

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   subscribed означает, что выгружает из списка подписок пользователя или остальных
    :param state:           Объект, который хранит состояние FSM для пользователя
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.model_dump_json()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = from_user.id

    subscribed = callback_data.subscribed
    page = callback_data.page
    subject = callback_data.subject
    user_subject_subscription = subject.subject_subscription_db

    if subscribed:
        subjects = await user_subject_subscription.get_subscription_df(user_id)
        await state.set_state(ChooseSubject.choosing_from_subscribed)
    else:
        subjects = pd.DataFrame(columns=['id', 'name'])
        await state.set_state(ChooseSubject.choosing_from_all_not_subscribed)

    await state.update_data(subject=subject)
    page_data, page_info, max_pages = get_page_data_and_info(subjects, page)
    keyboard = keyboards.get_subjects_list_kb(page_data, page, max_pages, subscribed, subject)

    if subscribed:
        msg_text = f'Выберите {subject.subject_name} из списка ваших подписок\n<b>{page_info}</b>'
    else:
        msg_text = f'Для поиска введите сообщение с именем {subject.subject_name_genitive}.'

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(ChooseSubject.choosing_from_subscribed)
@router.message(ChooseSubject.choosing_from_all_not_subscribed)
async def find_subject_by_name(
        message: types.Message,
        state: FSMContext,
) -> None:
    """
    Поиск по клиентам/сырью, на которые пользователь подписаны

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state:   Объект, который хранит состояние FSM для пользователя
    """
    subscribed = await state.get_state() == ChooseSubject.choosing_from_subscribed.state
    data = await state.get_data()
    subject: callback_data_factories.NewsItems = data.get('subject', None)

    if subject is None:
        msg_text = 'Пожалуйста, перезапустите меню новостей'
        await message.answer(msg_text)
        return

    subject_db = subject.subject_db
    user_subject_subscription = subject.subject_subscription_db

    fuzzy_searcher = FuzzyAlternativeNames(logger=logger)
    subject_ids = await fuzzy_searcher.find_subjects_id_by_name(message.text, subject_types=[subject_db.table_alternative])
    subjects = await subject_db.get_by_ids(subject_ids)
    subject_subscriptions = await user_subject_subscription.get_subscription_df(message.chat.id)

    if subscribed:
        subjects = subjects[subjects['id'].isin(subject_subscriptions['id'])]
    else:
        subjects = subjects[~subjects['id'].isin(subject_subscriptions['id'])]

    if len(subjects) > 1:
        page_data, page_info, max_pages = get_page_data_and_info(subjects)
        keyboard = keyboards.get_subjects_list_kb(page_data, 0, max_pages, subscribed, subject)
        msg_text = f'Выберите {subject.subject_name} из списка'
    elif len(subjects) == 1:
        subject_id = subjects['id'].iloc[0]
        interface = None
        for subject_interface in callback_data_factories.SubjectsInterfaces:
            if subject_interface.interface == subject_db:
                interface = subject_interface
                break

        back_callback_data = callback_data_factories.SubjectData(
            menu=callback_data_factories.NewsMenusEnum.subjects_list,
            back_menu=callback_data_factories.NewsMenusEnum.choose_subs_or_unsubs,
            subscribed=subscribed,
            subject=subject,
        )
        await answer_choose_period(message, back_callback_data, interface, [subject_id])
        return
    else:
        msg_text = 'Не нашелся, введите имя по-другому'
        keyboard = None

    await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(callback_data_factories.SubjectData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.choose_period_for_subject
))
async def choose_period_for_subject(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.SubjectData,
) -> None:
    """
    Выбор периода для получения новостей.

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    subject_db = callback_data.subject.subject_db

    callback_data.subject_ids = str(callback_data.subject_id)
    for subject in callback_data_factories.SubjectsInterfaces:
        if subject.interface == subject_db:
            callback_data.interface = subject
            break
    await choose_period(callback_query, callback_data)


@router.callback_query(callback_data_factories.TelegramGroupData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.choose_period_for_telegram
))
async def choose_period_for_telegram(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.TelegramGroupData,
) -> None:
    """
    Выбор периода для получения новостей.

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    if not callback_data.is_external_sources:
        callback_data.interface = callback_data_factories.SubjectsInterfaces.telegram
        get_news_handler = callback_data_factories.NewsMenusEnum.news_by_period
    else:
        callback_data.interface = callback_data_factories.SubjectsInterfaces.industry
        section = await telegram_section_db.get(callback_data.telegram_section_id)
        industry_info = await industry.get_by_name(section.name)

        callback_data.subject_ids = str(industry_info.id)
        callback_data.back_menu = callback_data_factories.NewsMenusEnum.choose_source_group
        get_news_handler = callback_data_factories.NewsMenusEnum.industry_news_by_period
    await choose_period(callback_query, callback_data, get_news_handler)


async def choose_period(
        callback_query: types.CallbackQuery,
        callback_data: Union[callback_data_factories.NewsMenuData,
                             callback_data_factories.TelegramGroupData,
                             callback_data_factories.SubjectData],
        get_news_handler: callback_data_factories.NewsMenusEnum = callback_data_factories.NewsMenusEnum.news_by_period,
) -> None:
    """
    Выбор периода для получения новостей.

    :param callback_query:      Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:       subscribed означает, что выгружает из списка подписок пользователя или остальных
    :param get_news_handler:    обработчик получения новостей
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    callback_data.menu = callback_data.back_menu
    await answer_choose_period(
        callback_query,
        callback_data,
        callback_data.interface,
        utils.get_selected_ids_from_callback_data(callback_data),
        get_news_handler,
    )
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def answer_choose_period(
        message: types.CallbackQuery | types.Message,
        back_menu: callback_data_factories.NewsMenuData,
        subject_interface: callback_data_factories.SubjectsInterfaces,
        selected_ids: list[int],
        get_news_handler: callback_data_factories.NewsMenusEnum = callback_data_factories.NewsMenusEnum.news_by_period,
) -> None:
    """
    Выбор периода для получения новостей.

    :param message:             Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param back_menu:           callback_data для кнопки Назад
    :param subject_interface:   SubjectInterface обработчик выдачи новостей за период
    :param selected_ids:        id выбранных субъектов, по которым надо получить новости
    :param get_news_handler:    обработчик получения новостей
    """
    selected = {i: (await subject_interface.interface.get(i))['name'] for i in selected_ids}

    keyboard = keyboards.get_periods_kb(
        periods=constants.GET_NEWS_PERIODS,
        subject_interface=subject_interface,
        selected_ids=utils.wrap_selected_ids(selected_ids),
        back_menu=back_menu,
        get_news_handler=get_news_handler,
    )
    msg_text = f'Выберите период для получения новостей по <b>{", ".join(selected.values())}</b>'
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(callback_data_factories.NewsMenuData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.news_by_period
))
async def get_subject_news_by_period(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.NewsMenuData,
) -> None:
    """
    Получение новостей за выбранный период

    Отправляет копию меню в конце, если были отправлены новости

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    days = callback_data.days_count

    to_date = datetime.datetime.now()
    from_date = to_date - datetime.timedelta(days=days)

    subject_db: SubjectInterface = callback_data.interface.interface
    selected = {i: (await subject_db.get(i))['name'] for i in utils.get_selected_ids_from_callback_data(callback_data)}

    articles = await subject_db.get_articles_by_subject_ids(
        list(selected.keys()),
        from_date,
        to_date,
        order_by=models.Article.date.desc(),
    )
    if not articles:
        msg_text = f'Новости по <b>{", ".join(selected.values())}</b> за {days} дней отсутствуют'
        await callback_query.message.answer(msg_text, parse_mode='HTML')
    else:
        for subject_id, articles_by_subject_id in groupby(articles, lambda x: x[1]):
            subject_name = selected[subject_id]
            frmt_msg = f'<b>{subject_name.capitalize()}</b>'
            msg_text = f'Новости по {frmt_msg} за {days} дней\n'

            all_articles = '\n\n'.join(
                FormatText(
                    title=article.title, date=article.date, link=article.link, text_sum=article.text_sum
                ).make_subject_text()
                for article, _ in articles_by_subject_id
            )
            frmt_msg += f'\n\n{all_articles}'
            await callback_query.message.answer(msg_text, parse_mode='HTML')
            await bot_send_msg(callback_query.bot, from_user.id, frmt_msg)
            await asyncio.sleep(1)
        await send_full_copy_of_message(callback_query)

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(callback_data_factories.NewsMenuData.filter(
    F.menu == callback_data_factories.NewsMenusEnum.industry_news_by_period
))
async def get_industry_news_by_period(
        callback_query: types.CallbackQuery,
        callback_data: callback_data_factories.NewsMenuData,
) -> None:
    """
    Получение новостей за выбранный период

    Отправляет копию меню в конце, если были отправлены новости

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data:   subscribed означает, что выгружает из списка подписок пользователя или остальных
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    industry_info = await industry.industry_db.get(int(callback_data.subject_ids))

    ap_obj = ArticleProcess(logger)
    tmdelta = datetime.timedelta(days=callback_data.days_count)

    clients_news = ap_obj.get_news_by_time(tmdelta, 'client').sort_values(by=['name', 'date'], ascending=[True, False])
    commodity_news = ap_obj.get_news_by_time(tmdelta, 'commodity').sort_values(by=['name', 'date'], ascending=[True, False])

    cols = ['name', 'date', 'link', 'title', 'text_sum', 'industry_id']
    all_article = pd.concat([clients_news[cols], commodity_news[cols]], ignore_index=True)
    industry_article_df = all_article[all_article['industry_id'] == industry_info['id']].drop_duplicates(subset='link')
    industry_article_df.insert(0, 'industry', industry_info['name'])
    industry_article_df['date'] = ''

    msg_text = f'Новости по отрасли <b>{industry_info["name"]}</b> за {callback_data.days_count} дней'
    if not industry_article_df.empty:
        await callback_query.message.answer(msg_text, parse_mode='HTML')
        msg = ArticleProcess.make_format_industry_msg(industry_article_df.values.tolist())
        await bot_send_msg(callback_query.bot, from_user.id, msg)
        await send_full_copy_of_message(callback_query)
    else:
        msg_text += ' отсутствуют'
        await callback_query.message.answer(msg_text, parse_mode='HTML')

    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
