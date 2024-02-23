import asyncio
# import logging

import pandas as pd
from aiogram import F, Router, types
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder

import config
from bot_logger import logger, user_logger
from constants.bot.aliases import (
    bonds_aliases,
    eco_aliases,
    exchange_aliases,
    metal_aliases,
    view_aliases, help_aliases, gigachat_aliases,
)
from constants.bot.constants import PATH_TO_COMMODITY_GRAPH
from handlers import common, quotes, gigachat
from module import data_transformer as dt
from module.article_process import ArticleProcess
from utils.bot.base import __create_fin_table, bot_send_msg, user_in_whitelist

# logger = logging.getLogger(__name__)
from utils.bot.newsletter import subscriptions_newsletter
from utils.db_api import research_source

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


class NextNewsCallback(CallbackData, prefix='next_news'):
    subject: str
    subject_id: int
    user_msg: str
    offset: int


@router.callback_query(NextNewsCallback.filter())
async def send_next_news(call: types.CallbackQuery, callback_data: NextNewsCallback) -> None:
    """Отправляет пользователю еще новостей по client или commodity"""
    subject_id = callback_data.subject_id
    subject = callback_data.subject
    limit_all = config.NEWS_LIMIT * 2 + 1
    offset_all = callback_data.offset
    user_msg = callback_data.user_msg
    callback_values = call.from_user
    full_name = f"{callback_values.first_name} {callback_values.last_name or ''}"
    chat_id = call.message.chat.id

    if not subject_id or not subject:
        return

    try:
        limit_all = int(limit_all)
        offset_all = int(offset_all)
    except (ValueError, TypeError):
        return

    ap_obj = ArticleProcess(logger)

    com_price, reply_msg, img_name_list = ap_obj.process_user_alias(subject_id, subject, limit_all, offset_all)
    new_offset = offset_all + config.NEWS_LIMIT * 2

    if reply_msg and isinstance(reply_msg, str):
        articles_all = reply_msg.split('\n\n', limit_all)
        if len(articles_all) > limit_all:
            articles_f5 = '\n\n'.join(articles_all[:limit_all])
            keyboard = InlineKeyboardBuilder()
            try:
                callback_meta = NextNewsCallback(
                    subject_id=subject_id,
                    subject=subject,
                    user_msg=user_msg,
                    offset=new_offset,
                )
            except ValueError:
                callback_meta = NextNewsCallback(
                    subject_id=subject_id,
                    subject=subject,
                    user_msg='',
                    offset=new_offset,
                )
            keyboard.add(types.InlineKeyboardButton(text='Еще новости', callback_data=callback_meta.pack()))
            keyboard = keyboard.as_markup()
        else:
            articles_f5 = reply_msg
            keyboard = None

        if len(articles_f5.encode()) < 4050:
            await call.message.answer(
                articles_f5, parse_mode='HTML', protect_content=False, disable_web_page_preview=True, reply_markup=keyboard
            )
        else:
            articles = articles_f5.split('\n\n')
            articles_len = len(articles)
            callback_markup = None
            for i, article in enumerate(articles, 1):
                if len(article.encode()) < 4050:
                    if i == articles_len:
                        callback_markup = keyboard
                    await call.message.answer(
                        article, parse_mode='HTML', protect_content=False, disable_web_page_preview=True, reply_markup=callback_markup
                    )
                    await asyncio.sleep(1.1)  # otherwise flood control return us 429 error
                else:
                    logger.error(f'MessageIsTooLong ERROR: {article}')

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


@router.message(Command('dailynews'))
async def dailynews(message: types.Message) -> None:
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.critical(f'*{chat_id}* {full_name} - {user_msg}. МЕТОД НЕ РАЗРЕШЕН!')
    user_df = pd.DataFrame([[message.from_user.id, full_name, '']], columns=['user_id', 'username', 'subscriptions'])
    await subscriptions_newsletter(message.bot, user_df, client_hours=20, commodity_hours=20)


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

    base_url = f'{config.research_base_url}group/guest/money'
    weekly_pulse_date_str = research_source.get_source_last_update_datetime(source_name='Weekly Pulse', source_link=base_url).strftime(config.BASE_DATE_FORMAT)
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
    ap_obj = ArticleProcess(logger=logger)
    nearest_subjects = ap_obj.find_nearest_to_subject(user_msg)

    cancel_command = 'отмена'
    buttons = [
        [types.KeyboardButton(text=cancel_command)],
        [types.KeyboardButton(text='Спросить у GigaChat')],
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


@router.message(F.text)
async def find_news(message: types.Message, state: FSMContext, prompt: str = '', return_ans: bool = False) -> None:
    """Обработка пользовательского сообщения"""

    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        ap_obj = ArticleProcess(logger)
        msg_text = message.text.replace('«', '"').replace('»', '"')

        # проверка пользовательского сообщения на запрос новостей по отраслям
        subject_ids, subject = ap_obj.find_subject_id(msg_text, 'industry'), 'industry'
        if subject_ids:
            industry_id = subject_ids[0]
            not_use, reply_msg, not_use_ = ap_obj.process_user_alias(industry_id, subject)
            await bot_send_msg(message.bot, chat_id, reply_msg)
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : получил новости по отраслям')
            return

        # проверка пользовательского сообщения на запрос новостей по клиентам/товарам
        subject_ids, subject = ap_obj.find_subject_id(msg_text, 'client'), 'client'
        if not subject_ids:
            subject_ids, subject = ap_obj.find_subject_id(msg_text, 'commodity'), 'commodity'

        for subject_id in subject_ids:
            com_price, reply_msg, img_name_list = ap_obj.process_user_alias(subject_id, subject)

            return_ans = await show_client_fin_table(message, subject_id, '', ap_obj)

            if reply_msg:

                if img_name_list:
                    await message.bot.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)
                    media = MediaGroupBuilder()
                    for name in img_name_list:
                        media.add_photo(types.FSInputFile(PATH_TO_COMMODITY_GRAPH.format(name)))
                    await message.answer_media_group(media=media.build(), protect_content=False)

                if com_price:
                    await message.answer(com_price, parse_mode='HTML', protect_content=False, disable_web_page_preview=True)

                if isinstance(reply_msg, str):
                    articles_all = reply_msg.split('\n\n', config.NEWS_LIMIT + 1)
                    if len(articles_all) > config.NEWS_LIMIT + 1:
                        articles_f5 = '\n\n'.join(articles_all[: config.NEWS_LIMIT + 1])
                        keyboard = InlineKeyboardBuilder()
                        try:
                            callback_meta = NextNewsCallback(
                                subject_id=subject_id,
                                subject=subject,
                                user_msg=user_msg,
                                offset=config.NEWS_LIMIT,
                            )
                        except ValueError:
                            callback_meta = NextNewsCallback(
                                subject_id=subject_id,
                                subject=subject,
                                user_msg='',
                                offset=config.NEWS_LIMIT,
                            )
                        keyboard.add(types.InlineKeyboardButton(text='Еще новости', callback_data=callback_meta.pack()))
                        keyboard = keyboard.as_markup()
                    else:
                        articles_f5 = reply_msg
                        keyboard = None

                    try:
                        await message.answer(
                            articles_f5, parse_mode='HTML', protect_content=False, disable_web_page_preview=True, reply_markup=keyboard
                        )
                    # except MessageIsTooLong:  # FIXME 3.3.0
                    #     articles = articles_f5.split('\n\n')
                    #     for article in articles:
                    #         if len(article) < 4050:
                    #             await message.answer(article, parse_mode='HTML', protect_content=False, disable_web_page_preview=True)
                    #         else:
                    #             logger.error(f'MessageIsTooLong ERROR: {article}')
                    except Exception as e:
                        logger.error(f'ERROR *{chat_id}* {msg_text} - {e}')

                user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : получил новости по {subject}')
                return_ans = True

        if not return_ans:
            return_ans = await show_client_fin_table(message, 0, msg_text, ap_obj)

        if return_ans:
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg} : получил таблицу фин показателей')
        else:
            aliases_dict = {
                **{alias: (common.help_handler, {}) for alias in help_aliases},
                **{alias: (gigachat.set_gigachat_mode, {'state': state}) for alias in gigachat_aliases},
                **{alias: (quotes.bonds_info, {}) for alias in bonds_aliases},
                **{alias: (quotes.economy_info, {}) for alias in eco_aliases},
                **{alias: (quotes.metal_info, {}) for alias in metal_aliases},
                **{alias: (quotes.exchange_info, {}) for alias in exchange_aliases},
                **{alias: (quotes.data_mart, {}) for alias in view_aliases},
            }
            message_text = message.text.lower().strip()
            function_to_call, kwargs = aliases_dict.get(message_text, (None, None))
            if function_to_call:
                await function_to_call(message, **kwargs)
            else:
                await state.set_state(gigachat.GigaChatState.gigachat_query)
                await state.update_data(gigachat_query=message.text)
                await send_nearest_subjects(message)

    else:
        await message.answer('Неавторизованный пользователь. Отказано в доступе.', protect_content=False)
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
