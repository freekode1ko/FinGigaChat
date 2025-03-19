"""Хендлеры новостей новостей новостей"""
from aiogram import Bot, F, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from fuzzywuzzy import process
from sqlalchemy.ext.asyncio import AsyncSession

import utils.base
from configs import config
from constants import aliases, enums
from constants.texts.texts_manager import texts_manager
from db import models, parser_source
from db.api import stakeholder
from db.api.client import client_db, get_research_type_id_by_name
from db.api.commodity import commodity_db
from db.api.industry import industry_db
from db.api.subject_interface import SubjectInterface
from handlers import common, quotes
from handlers.ai.rag import rag
from handlers.analytics import analytics_sell_side
from handlers.clients.callback_data_factories import ClientsMenuData, ClientsMenusEnum
from handlers.clients.keyboards import get_client_menu_kb, get_stakeholder_menu_kb
from handlers.clients.utils import get_menu_msg_by_sh_type, get_show_msg_by_sh_type, is_client_in_message
from handlers.commodity.utils import is_commodity_in_message
from handlers.news.handler import router
from keyboards.news import callbacks
from log.bot_logger import logger, user_logger
from module import data_transformer as dt
from module.article_process import ArticleProcess
from module.fuzzy_search import FuzzyAlternativeNames
from utils.base import bot_send_msg, send_or_edit
from utils.decorators import has_access_to_feature
from utils.function_calling.tools import find_and_run_tool_function
from utils.handler_utils import audio_to_text


class StakeholderState(StatesGroup):
    """Состояние для возвращения к меню стейкхолдера."""

    choosing_from_stakeholder = State()


class NextNewsCallback(CallbackData, prefix='next_news'):
    """CallbackData для следующей новости"""

    subject: str
    subject_id: int
    offset: int
    limit: int


async def send_news_with_next_button(
        bot: Bot,
        chat_id: int,
        reply_msg: str,
        subject_id: int,
        subject: str,
        next_news_offset: int,
        articles_limit: int,
) -> None:
    """
    Отправка новостей по клиенту, сырью и отрасли (reply_msg).

    :param bot: Объект телеграм бота aiogram.Bot
    :param chat_id: Чат, в который нужно отправить новости
    :param reply_msg: Новости, разделенные двойным переносом строки
    :param subject_id: id клиента или сырья, или отрасли
    :param subject: название таблицы объекта (client, commodity, industry)  FIXME Enum
    :param next_news_offset: Данные для формирование кнопки Еще новости
    :param articles_limit: Кол-во новостей, которые надо отправить
    """
    articles_all = reply_msg.split('\n\n', articles_limit)
    if len(articles_all) > articles_limit:
        articles_upto_limit = '\n\n'.join(articles_all[:articles_limit + 1])
        keyboard = InlineKeyboardBuilder()
        callback_meta = NextNewsCallback(
            subject_id=subject_id,
            subject=subject,
            offset=next_news_offset,
            limit=articles_limit,
        )
        keyboard.add(types.InlineKeyboardButton(text='Еще новости', callback_data=callback_meta.pack()))
        keyboard = keyboard.as_markup()
    else:
        articles_upto_limit = reply_msg
        keyboard = None

    sent_messages = await bot_send_msg(bot, chat_id, articles_upto_limit)
    if keyboard:
        await bot.edit_message_reply_markup(
            chat_id=chat_id,
            message_id=sent_messages[-1].message_id,
            reply_markup=keyboard
        )


@router.callback_query(NextNewsCallback.filter())
async def send_next_news(call: types.CallbackQuery, callback_data: NextNewsCallback) -> None:
    """Отправляет пользователю еще новостей по client или commodity"""
    subject_id = callback_data.subject_id
    subject = callback_data.subject
    limit_all = callback_data.limit
    offset_all = callback_data.offset
    user_msg = callback_data.pack()

    callback_values = call.from_user
    full_name = f"{callback_values.first_name} {callback_values.last_name or ''}"
    chat_id = call.message.chat.id

    if not subject_id or not subject:
        return

    ap_obj = ArticleProcess(logger)

    _, reply_msg = await ap_obj.process_user_alias(subject_id, subject, limit_all, offset_all)
    new_offset = offset_all + callback_data.limit

    if reply_msg and isinstance(reply_msg, str):
        await send_news_with_next_button(call.bot, chat_id, reply_msg, subject_id, subject, new_offset, limit_all)
        await call.message.edit_reply_markup()

        user_logger.info(
            f'*{chat_id}* {full_name} - {user_msg} : получил следующий набор новостей по {subject} (всего {new_offset})'
        )


@router.message(Command('newsletter'))
@has_access_to_feature(enums.FeatureType.analytics_menu)
async def show_newsletter_buttons(message: types.Message) -> None:
    """Отображает кнопки с доступными рассылками"""
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    newsletter_dict = dt.Newsletter.get_newsletter_dict()  # {тип рассылки: заголовок рассылки}
    callback_func = 'send_newsletter_by_button'  # функция по отображению рассылки

    keyboard = InlineKeyboardBuilder()
    for type_, title in newsletter_dict.items():
        callback = f'{callback_func}:{type_}'
        keyboard.row(types.InlineKeyboardButton(text=title, callback_data=callback))

    await message.answer('Какую информацию вы хотите получить?', reply_markup=keyboard.as_markup())
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith('send_newsletter_by_button'))
async def send_newsletter_by_button(callback_query: types.CallbackQuery) -> None:
    """Отправляет рассылку по кнопке"""
    # получаем данные
    newsletter_type = callback_query.data.split(':')[1]
    user_id = callback_query.from_user.id

    # получаем текст рассылки
    if newsletter_type == 'weekly_result':
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_result()
    elif newsletter_type == 'weekly_event':
        title, newsletter, img_path_list = dt.Newsletter.make_weekly_event()
    else:
        return

    weekly_pulse_date_str = parser_source.get_source_last_update_datetime(source_name='Weekly Pulse').strftime(config.BASE_DATE_FORMAT)
    weekly_pulse_date_str = texts_manager.COMMON_DATE_OF_DATA.format(date=weekly_pulse_date_str)

    media = MediaGroupBuilder(caption=weekly_pulse_date_str)
    for path in img_path_list:
        media.add_photo(types.FSInputFile(path))
    await callback_query.message.answer(
        text=newsletter,
        parse_mode='HTML',
        # protect_content=texts_manager.PROTECT_CONTENT,
    )
    await callback_query.message.answer_media_group(
        media=media.build(),
        # protect_content=texts_manager.PROTECT_CONTENT,
    )
    user_logger.debug(f'*{user_id}* Пользователю пришла рассылка "{title}" по кнопке')


@has_access_to_feature(enums.FeatureType.news)
async def send_nearest_subjects(message: types.Message, user_msg: str, features: dict[str, bool]) -> None:
    """Отправляет пользователю близкие к его запросу названия clients или commodities"""
    chat_id, full_name = message.chat.id, message.from_user.full_name
    fuzzy_searcher = FuzzyAlternativeNames()

    if features.get(enums.FeatureType.company_menu):
        nearest_subjects = await fuzzy_searcher.find_nearest_to_subject(user_msg)
    else:
        nearest_subjects = await fuzzy_searcher.find_nearest_to_subject(
            user_msg,
            subject_types=[models.CommodityAlternative, models.IndustryAlternative]
        )

    buttons = [[types.KeyboardButton(text=texts_manager.COMMON_CANCEL_WORD)], ]
    if features.get(enums.FeatureType.knowledgebase):
        buttons.append([types.KeyboardButton(text=texts_manager.RAG_ASK_KNOWLEDGE)])

    for subject_name in nearest_subjects:
        buttons.append([types.KeyboardButton(text=subject_name)])

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder=texts_manager.COMMON_CANCEL_MSG,
        one_time_keyboard=True
    )

    await message.answer(
        texts_manager.COMMON_CLARIFYING_REQUEST,
        parse_mode='HTML',
        # protect_content=texts_manager.PROTECT_CONTENT,
        disable_web_page_preview=True,
        reply_markup=keyboard,
    )
    user_logger.info(
        f'*{chat_id}* {full_name} - "{user_msg}" : На запрос пользователя найдены схожие запросы {", ".join(nearest_subjects)}'
    )


@has_access_to_feature(feature=enums.FeatureType.analytics_menu, is_need_answer=False)
async def send_client_navi_link(message: types.Message, client_id: int, ap_obj: ArticleProcess) -> None:
    """
    Отправляет сообщение с ссылкой на invaigator клиента

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param client_id: id клиента (client.id)
    :param ap_obj: Объект, который ищет и форматирует новости
    """
    try:
        name, navi_link = ap_obj.get_client_name_and_navi_link(client_id)
        if navi_link is not None:
            await message.answer(
                texts_manager.ANAL_NAVI_LINK.format(link=navi_link, name=name),
                parse_mode='HTML',
            )
            await message.answer(texts_manager.NAVI_LINK_HELP, parse_mode='HTML')
    except Exception as e:
        logger.error(f'ERROR *{message.chat.id}* {message.text} - {e}')


@has_access_to_feature(feature=enums.FeatureType.news, is_need_answer=False)
async def send_news(message: types.Message, user_msg: str, full_name: str) -> bool:
    """Отправка новостей по клиенту/сырьевому товару/отрасли"""
    chat_id = message.chat.id

    ap_obj = ArticleProcess(logger)
    msg_text = (
        user_msg.replace('«', '"').replace('»', '"')
        .replace(texts_manager.CLIENT_ADDITIONAL_INFO, '')
        .replace(texts_manager.COMMODITY_ADDITIONAL_INFO, '')
        .replace(texts_manager.INDUSTRY_ADDITIONAL_INFO, '')
        .replace(texts_manager.STAKEHOLDER_ADDITIONAL_INFO, '')
    )

    return_ans = False

    # проверка пользовательского сообщения на запрос новостей по отраслям
    subject_ids, subject = ap_obj.find_subject_id(msg_text, 'industry'), 'industry'
    if subject_ids:
        industry_id = subject_ids[0]
        _, reply_msg = await ap_obj.process_user_alias(industry_id, subject)
        await bot_send_msg(message.bot, chat_id, reply_msg)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : получил новости по отраслям')
        return True

    # проверка пользовательского сообщения на запрос новостей по клиентам/товарам
    subject_ids, subject = ap_obj.find_subject_id(msg_text, 'client'), 'client'
    if not subject_ids:
        subject_ids, subject = ap_obj.find_subject_id(msg_text, 'commodity'), 'commodity'

    for subject_id in subject_ids:
        com_price, reply_msg = await ap_obj.process_user_alias(subject_id, subject)

        if not reply_msg:
            continue

        if com_price:
            await message.answer(com_price, parse_mode='HTML', disable_web_page_preview=True)

        if isinstance(reply_msg, str):
            await send_news_with_next_button(
                message.bot, chat_id, reply_msg, subject_id, subject, config.OTHER_NEWS_COUNT, config.NEWS_LIMIT
            )

            if subject == 'client':
                await send_client_navi_link(message, subject_id, ap_obj)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : получил новости по {subject}')
        return_ans = True

    return return_ans


async def get_subject_news(
        callback_query: types.CallbackQuery,
        callback_data: CallbackData,
        subject_db_api: SubjectInterface,
) -> None:
    """
    Получение имени subject и отправка новостей по нему

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит id объекта, по которому вынимаются новости
    :param subject_db_api: Интерфейс взаимодействия с таблицами клиентов/сырья/отраслей
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_data.pack()
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    client_id = callback_data.subject_id
    subject = await subject_db_api.get(client_id)
    await send_news(callback_query.message, subject['name'], full_name)


@router.callback_query(callbacks.GetClientNews.filter())
async def get_client_news(callback_query: types.CallbackQuery, callback_data: callbacks.GetClientNews) -> None:
    """
    Получение новостей по клиенту

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе инфу о id клиента
    """
    await get_subject_news(callback_query, callback_data, client_db)
    await utils.base.send_full_copy_of_message(callback_query)


@router.callback_query(callbacks.GetCommodityNews.filter())
async def get_commodity_news(callback_query: types.CallbackQuery, callback_data: callbacks.GetCommodityNews) -> None:
    """
    Получение новостей по сырьевому товару

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе инфу о id сырья
    """
    await get_subject_news(callback_query, callback_data, commodity_db)
    await utils.base.send_full_copy_of_message(callback_query)


@router.callback_query(callbacks.GetIndustryNews.filter())
async def get_industry_news(callback_query: types.CallbackQuery, callback_data: callbacks.GetIndustryNews) -> None:
    """
    Получение новостей по отрасли

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе инфу о id отрасли
    """
    await get_subject_news(callback_query, callback_data, industry_db)
    await utils.base.send_full_copy_of_message(callback_query)


@has_access_to_feature(feature=enums.FeatureType.analytics_menu, is_need_answer=False)
async def is_eco_in_message(
        message: types.Message,
        user_msg: str,
        score_cutoff: int = config.ECO_FUZZY_SEARCH_SCORE_CUTOFF,
) -> bool:
    """
    Есть ли ETC в тексте сообщения.

    Проверяет сходство сообщения пользователя с единые трансфертные ставки.
    Если процент совпадения выше score_cutoff, то выдает ссылку на inavigator.

    :param message:       Объект, содержащий сообщение пользователя и инфу о пользователе
    :param user_msg:      Сообщение пользователя
    :param score_cutoff:  Минимальный требуемый процент совпадения
    :return:              Есть ли ЕТС в тексте сообщения
    """
    if flag := bool(process.extractOne(user_msg.lower(), aliases.ECO_NAMES, score_cutoff=score_cutoff)):
        msg_text = f'<a href="{config.ECO_INAVIGATOR_URL}">Актуальные ETC</a>'  # TODO: add to quotes redis texts?
        await message.answer(
            msg_text,
            parse_mode='HTML',
            # protect_content=False,
        )
        await message.answer(texts_manager.NAVI_LINK_HELP, parse_mode='HTML')
    return flag


@router.message(F.content_type.in_({'voice', 'text'}))
@has_access_to_feature(enums.FeatureType.common)
async def process_user_message(
        message: types.Message,
        state: FSMContext,
        session: AsyncSession,
        features: dict[str, bool]
) -> None:
    """Обработка пользовательского сообщения"""
    chat_id, full_name = message.chat.id, message.from_user.full_name

    if message.voice:
        user_msg = await audio_to_text(message)
    else:
        user_msg = message.text

    if await find_and_run_tool_function(message, user_msg):
        return

    if (
            await is_client_in_message(message, user_msg) or
            await is_stakeholder_in_message(message, user_msg, state, session) or
            await is_eco_in_message(message, user_msg) or
            await is_commodity_in_message(message, user_msg)
    ):
        return

    return_ans = await send_news(message, user_msg, full_name)

    if return_ans:
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : получил новости')
    else:
        aliases_dict = {
            **{alias: (common.help_handler, {'state': state, 'user_msg': user_msg}) for alias in aliases.help_aliases},
            **{alias: (rag.set_rag_mode, {'state': state, 'session': session}) for alias in aliases.giga_and_rag_aliases},
            **{alias: (common.open_meeting_app, {}) for alias in aliases.web_app_aliases},
            **{alias: (quotes.bonds_info_command, {}) for alias in aliases.bonds_aliases},
            **{alias: (quotes.economy_info_command, {}) for alias in aliases.eco_aliases},
            **{alias: (quotes.metal_info_command, {}) for alias in aliases.metal_aliases},
            **{alias: (quotes.exchange_info_command, {}) for alias in aliases.exchange_aliases},
            **{alias: (analytics_sell_side.data_mart_body, {}) for alias in aliases.view_aliases},
        }
        message_text = user_msg.lower().strip()
        function_to_call, kwargs = aliases_dict.get(message_text, (None, None))
        if function_to_call:
            await function_to_call(message, **kwargs)
        else:
            await state.set_state(rag.RagState.rag_user_msg)
            await state.update_data(rag_user_msg=message)
            await send_nearest_subjects(message, user_msg, features)


@has_access_to_feature(feature=enums.FeatureType.company_menu, is_need_answer=False)
async def is_stakeholder_in_message(
        message: types.Message,
        user_msg: str,
        state: FSMContext,
        session: AsyncSession,
        fuzzy_score: int = 95
) -> bool:
    """
    Является ли введенное сообщение стейкхолдером, и если да, вывод меню стейкхолдера или новостей.

    :param message:      Сообщение от пользователя.
    :param user_msg:     Сообщение пользователя
    :param state:        Состояние пользователя.
    :param session:      Сессия для взаимодействия с бд.
    :param fuzzy_score:  Величина в процентах совпадение с референтными именами стейкхолдеров.
    :return:             Булевое значение о том что совпадает ли сообщение с именем стейкхолдера.
    """
    sh_ids = await FuzzyAlternativeNames().find_subjects_id_by_name(
        user_msg.replace(texts_manager.STAKEHOLDER_ADDITIONAL_INFO, ''),
        subject_types=[models.StakeholderAlternative, ],
        score=fuzzy_score
    )

    if len(set(sh_ids)) != 1:
        return False

    sh_obj = await stakeholder.get_stakeholder_by_id(session, sh_ids[0])
    if not sh_obj.clients:  # такого случая по факту не должно быть
        await message.answer(texts_manager.NEWS_NOT_FOUND, reply_markeup=types.ReplyKeyboardRemove())
        return True

    stakeholder_types = await stakeholder.get_stakeholder_types(session, sh_obj.id)
    msg_text = get_menu_msg_by_sh_type(stakeholder_types, sh_obj)
    keyboard = get_stakeholder_menu_kb(sh_obj.clients)
    await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML')

    await state.set_state(StakeholderState.choosing_from_stakeholder)
    await state.update_data(stakeholder_id=sh_ids[0])

    return True


@router.callback_query(ClientsMenuData.filter(F.menu == ClientsMenusEnum.choose_stakeholder_clients))
async def choose_stakeholder_client(
        callback_query: types.CallbackQuery,
        callback_data: ClientsMenuData,
) -> None:
    """
    Отображение меню выбранного клиента стейкхолдера.

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param callback_data:   Информация о выбранной группе клиентов стейкхолдера.
    """
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    client_dict = await client_db.get(callback_data.client_id)
    client_name: str = client_dict['name']

    keyboard = get_client_menu_kb(
        callback_data.client_id,
        current_page=0,
        research_type_id=await get_research_type_id_by_name(client_name),
        with_back_button=True,
    )
    await send_or_edit(
        callback_query,
        texts_manager.CLIENT_CHOOSE_SECTION.format(name=client_name.capitalize()),
        keyboard
    )
    user_logger.info(f'*{chat_id}* {full_name} - {callback_data}')


@router.callback_query(ClientsMenuData.filter(F.menu == ClientsMenusEnum.show_news_from_sh))
async def show_stakeholder_articles(
        callback_query: types.CallbackQuery,
        session: AsyncSession,
        state: FSMContext
) -> None:
    """
    Отправка новостей по выбранным клиентам стейкхолдера.

    :param callback_query:  Объект, содержащий в себе информацию по отправителю, чату и сообщению.
    :param state:           Состояние пользователя.
    :param session:         Сессия для взаимодействия с бд.
    """
    data = await state.get_data()
    sh_obj = await stakeholder.get_stakeholder_by_id(session, data['stakeholder_id'])
    clients_ids = [c.id for c in sh_obj.clients]
    stakeholder_types = await stakeholder.get_stakeholder_types(session, data['stakeholder_id'])
    msg_text = get_show_msg_by_sh_type(stakeholder_types, sh_obj)
    await callback_query.message.edit_text(msg_text, parse_mode='HTML')

    ap_obj = ArticleProcess(logger)
    for client_id in clients_ids:
        await send_stakeholder_articles(callback_query, ap_obj, client_id)


async def send_stakeholder_articles(
        tg_obj: types.CallbackQuery | types.Message,
        ap_obj: ArticleProcess,
        client_id: int,
) -> None:
    """
    Отправка новостей о клиенте стейкхолдера.

    :param tg_obj:          Telegram-объект для отправки сообщения и получения данных о пользователе.
    :param ap_obj:          Экземпляр ArticleProcess.
    :param client_id:       ID клиента.
    """
    _, articles = await ap_obj.process_user_alias(
        subject=enums.SubjectType.client,
        subject_id=client_id,
        limit_val=config.NEWS_LIMIT_SH
    )
    await send_news_with_next_button(
        tg_obj.bot,
        tg_obj.from_user.id,
        articles,
        client_id,
        enums.SubjectType.client,
        config.OTHER_NEWS_COUNT_SH,
        config.NEWS_LIMIT_SH
    )
    user_logger.info(f'*{tg_obj.from_user.id}* {tg_obj.from_user.full_name} - получил новости по клиенту с id {client_id}')
