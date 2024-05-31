from aiogram import F, types, Bot
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.ext.asyncio import AsyncSession

import utils.base
from configs import config
from constants import aliases
from db import parser_source
from db.api.client import client_db
from db.api.commodity import commodity_db
from db.api.industry import industry_db
from db.api.subject_interface import SubjectInterface
from handlers import common, quotes
from handlers.ai.rag import rag
from handlers.analytics import analytics_sell_side
from handlers.clients.utils import is_client_in_message
from handlers.news.handler import router
from keyboards.news import callbacks
from log.bot_logger import logger, user_logger
from module import data_transformer as dt
from module.article_process import ArticleProcess
from module.fuzzy_search import FuzzyAlternativeNames
from utils.base import __create_fin_table, bot_send_msg, user_in_whitelist


class NextNewsCallback(CallbackData, prefix='next_news'):
    subject: str
    subject_id: int
    offset: int


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
    Отправка новостей по клиенту/сырью/отрасли (reply_msg).

    :param bot: Объект телеграм бота aiogram.Bot
    :param chat_id: Чат, в который нужно отправить новости
    :param reply_msg: Новости, разделенные \n\n
    :param subject_id: id клиента или сырья, или отрасли
    :param subject: название таблицы объекта (client, commodity, industry)  FIXME Enum
    :param next_news_offset: Данные для формирование кнопки Еще новости
    :param articles_limit: Кол-во новостей, которые надо отправить
    """
    articles_all = reply_msg.split('\n\n', articles_limit)
    if len(articles_all) > articles_limit:
        articles_upto_limit = '\n\n'.join(articles_all[:articles_limit])
        keyboard = InlineKeyboardBuilder()
        callback_meta = NextNewsCallback(
            subject_id=subject_id,
            subject=subject,
            offset=next_news_offset,
        )
        keyboard.add(types.InlineKeyboardButton(text='Еще новости', callback_data=callback_meta.pack()))
        keyboard = keyboard.as_markup()
    else:
        articles_upto_limit = reply_msg
        keyboard = None

    sent_messages = await utils.base.bot_send_msg(bot, chat_id, articles_upto_limit)
    await bot.edit_message_reply_markup(chat_id, message_id=sent_messages[-1].message_id, reply_markup=keyboard)


@router.callback_query(NextNewsCallback.filter())
async def send_next_news(call: types.CallbackQuery, callback_data: NextNewsCallback) -> None:
    """Отправляет пользователю еще новостей по client или commodity"""
    subject_id = callback_data.subject_id
    subject = callback_data.subject
    limit_all = config.NEWS_LIMIT + 1
    offset_all = callback_data.offset
    user_msg = callback_data.pack()

    callback_values = call.from_user
    full_name = f"{callback_values.first_name} {callback_values.last_name or ''}"
    chat_id = call.message.chat.id

    if not subject_id or not subject:
        return

    ap_obj = ArticleProcess(logger)

    _, reply_msg = await ap_obj.process_user_alias(subject_id, subject, limit_all, offset_all)
    new_offset = offset_all + config.NEWS_LIMIT

    if reply_msg and isinstance(reply_msg, str):
        await send_news_with_next_button(call.bot, chat_id, reply_msg, subject_id, subject, new_offset, limit_all)
        await call.message.edit_reply_markup()

        user_logger.info(
            f'*{chat_id}* {full_name} - {user_msg} : получил следующий набор новостей по {subject} ' f'(всего {new_offset})'
        )


async def show_client_fin_table(message: types.Message, s_id: int, msg_text: str, ap_obj: ArticleProcess) -> bool:
    """
    Вывод таблицы с финансовыми показателями в виде фотокарточки

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param s_id: ID клиента или комоды
    :param msg_text: Текст сообщения
    :param ap_obj: экземпляр класса ArticleProcess
    return значение об успешности создания таблицы
    """
    client_name, client_fin_table = ap_obj.get_client_fin_indicators(s_id, msg_text.strip().lower())
    if not client_fin_table.empty:
        await message.bot.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
        await __create_fin_table(message, client_name, client_fin_table)
        return True
    else:
        return False


@router.message(Command('newsletter'))
async def show_newsletter_buttons(message: types.Message) -> None:
    """Отображает кнопки с доступными рассылками"""

    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        newsletter_dict = dt.Newsletter.get_newsletter_dict()  # {тип рассылки: заголовок рассылки}
        callback_func = 'send_newsletter_by_button'  # функция по отображению рассылки

        keyboard = InlineKeyboardBuilder()
        for type_, title in newsletter_dict.items():
            callback = f'{callback_func}:{type_}'
            keyboard.row(types.InlineKeyboardButton(text=title, callback_data=callback))

        await message.answer('Какую информацию вы хотите получить?', reply_markup=keyboard.as_markup())

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


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
    weekly_pulse_date_str = f'Данные на {weekly_pulse_date_str}'

    media = MediaGroupBuilder(caption=weekly_pulse_date_str)
    for path in img_path_list:
        media.add_photo(types.FSInputFile(path))
    await callback_query.message.answer(text=newsletter, parse_mode='HTML', protect_content=True)
    await callback_query.message.answer_media_group(media=media.build(), protect_content=True)
    user_logger.debug(f'*{user_id}* Пользователю пришла рассылка "{title}" по кнопке')


async def send_nearest_subjects(message: types.Message) -> None:
    """Отправляет пользователю близкие к его запросу названия clients или commodities"""
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    fuzzy_searcher = FuzzyAlternativeNames(logger=logger)
    nearest_subjects = await fuzzy_searcher.find_nearest_to_subject(user_msg)

    cancel_command = 'отмена'
    buttons = [
        [types.KeyboardButton(text=cancel_command)],
        [types.KeyboardButton(text='Спросить у Базы Знаний')],
    ]
    for subject_name in nearest_subjects:
        buttons.append([types.KeyboardButton(text=subject_name)])

    cancel_msg = f'Напишите «{cancel_command}» для очистки'
    response = 'Уточните, пожалуйста, ваш запрос..\n\nВозможно, вы имели в виду один из следующих вариантов:'
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons, resize_keyboard=True, input_field_placeholder=cancel_msg, one_time_keyboard=True
    )

    await message.answer(response, parse_mode='HTML', protect_content=False, disable_web_page_preview=True, reply_markup=keyboard)
    user_logger.info(
        f'*{chat_id}* {full_name} - "{user_msg}" : На запрос пользователя найдены схожие запросы {", ".join(nearest_subjects)}'
    )


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
                f'<a href="{str(navi_link)}">Цифровая справка клиента: "{str(name)}"</a>',
                parse_mode='HTML',
            )
    except Exception as e:
        logger.error(f'ERROR *{message.chat.id}* {message.text} - {e}')


async def send_news(message: types.Message, user_msg: str, full_name: str) -> bool:
    """Отправка новостей по клиенту/сырьевому товару/отрасли"""
    chat_id = message.chat.id

    ap_obj = ArticleProcess(logger)
    msg_text = user_msg.replace('«', '"').replace('»', '"')

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

        return_ans = await show_client_fin_table(message, subject_id, '', ap_obj)

        if not reply_msg:
            continue

        if com_price:
            await message.answer(com_price, parse_mode='HTML', disable_web_page_preview=True)

        if isinstance(reply_msg, str):
            await send_news_with_next_button(message.bot, chat_id, reply_msg, subject_id, subject,
                                             config.OTHER_NEWS_COUNT, config.NEWS_LIMIT + 1)

            if subject == 'client':
                await send_client_navi_link(message, subject_id, ap_obj)

        user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : получил новости по {subject}')
        return_ans = True

    if not return_ans:
        return_ans = await show_client_fin_table(message, 0, msg_text, ap_obj)

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


@router.callback_query(callbacks.GetCommodityNews.filter())
async def get_commodity_news(callback_query: types.CallbackQuery, callback_data: callbacks.GetCommodityNews) -> None:
    """
    Получение новостей по сырьевому товару

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе инфу о id сырья
    """
    await get_subject_news(callback_query, callback_data, commodity_db)


@router.callback_query(callbacks.GetIndustryNews.filter())
async def get_industry_news(callback_query: types.CallbackQuery, callback_data: callbacks.GetIndustryNews) -> None:
    """
    Получение новостей по отрасли

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе инфу о id отрасли
    """
    await get_subject_news(callback_query, callback_data, industry_db)


@router.message(F.text)
async def find_news(message: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """Обработка пользовательского сообщения"""
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        if await is_client_in_message(message, user_logger):
            return

        return_ans = await send_news(message, user_msg, full_name)

        if return_ans:
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : получил таблицу фин показателей')
        else:
            aliases_dict = {
                **{alias: (common.help_handler, {}) for alias in aliases.help_aliases},
                **{alias: (rag.set_rag_mode, {'state': state, 'session': session}) for alias in aliases.giga_and_rag_aliases},
                **{alias: (common.open_meeting_app, {}) for alias in aliases.web_app_aliases},
                **{alias: (quotes.bonds_info, {}) for alias in aliases.bonds_aliases},
                **{alias: (quotes.economy_info, {}) for alias in aliases.eco_aliases},
                **{alias: (quotes.metal_info, {}) for alias in aliases.metal_aliases},
                **{alias: (quotes.exchange_info, {}) for alias in aliases.exchange_aliases},
                **{alias: (analytics_sell_side.data_mart_body, {}) for alias in aliases.view_aliases},
            }
            message_text = message.text.lower().strip()
            function_to_call, kwargs = aliases_dict.get(message_text, (None, None))
            if function_to_call:
                await function_to_call(message, **kwargs)
            else:
                await state.set_state(rag.RagState.rag_query)
                await state.update_data(rag_query=message.text)
                await send_nearest_subjects(message)

    else:
        await message.answer('Неавторизованный пользователь. Отказано в доступе.', protect_content=False)
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
