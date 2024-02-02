import json
from typing import List, Union

import pandas as pd
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import text

import config
from bot_logger import logger, user_logger
from constants.bot.constants import handbook_format, DELETE_CROSS, UNSELECTED, SELECTED
from constants.bot.subscriptions import BACK_TO_MENU, TG_SUBS_DELETE_ALL_DONE, TG_SUBS_DELETE_ALL, \
    TG_SUBS_INDUSTRIES_MENU, TG_CHANNEL_INFO, USER_TG_SUBS, TG_SUB_ACTION
from database import engine
from keyboards.subscriptions.callbacks import UserTGSubs, TGChannelMoreInfo, IndustryTGChannels, TGSubAction
from keyboards.subscriptions import constructors as kb_maker
from keyboards.subscriptions.constructors import get_tg_info_kb
from module.article_process import ArticleProcess
from utils.bot_utils import user_in_whitelist, get_page_data_and_info
from utils.db_api.industry import get_industries, get_industry_name
from utils.db_api.subscriptions import get_user_tg_subscriptions_df, delete_user_telegram_subscription, \
    delete_all_user_telegram_subscriptions, get_industry_tg_channels_df, get_telegram_channel_info, \
    add_user_telegram_subscription

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


class SubscriptionsStates(StatesGroup):
    user_subscriptions = State()
    delete_user_subscriptions = State()


async def add_subscriptions_body(
    message: types.Message, full_name: str, user_msg: str, from_user_json: str, state: FSMContext
) -> None:
    """
    Формирует ответное сообщение для добавления подписок

    :param chat_id: int - ID чата с пользователем
    :param full_name: str - имя пользователя (first_name + last_name)
    :param user_msg: str - сообщение пользователя
    :param from_user_json: str - данные из aiogram.types.Message.from_user.model_dump_json()
                                содержит ID пользователя и прочую информацию о пользователе
    :param state: Состояние FSM
    """
    chat_id = message.chat.id
    if await user_in_whitelist(from_user_json):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await state.set_state(SubscriptionsStates.user_subscriptions)
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text='Показать готовые подборки', callback_data='showmeindustry:yes'))
        keyboard.row(types.InlineKeyboardButton(text='Отменить создание подписок', callback_data='showmeindustry:no'))
        await message.answer(
            'Сформируйте полный список интересующих клиентов или commodities '
            'для подписки на пассивную отправку новостей по ним.\n'
            'Перечислите их в одном следующем сообщении каждую с новой строки.\n'
            '\nНапример:\nгаз\nгазпром\nнефть\nзолото\nбалтика\n\n'
            'Вы также можете воспользоваться готовыми подборками клиентов и commodities, '
            'которые отсортированы по отраслям. Скопируйте готовую подборку, исключите '
            'лишние наименования или добавьте дополнительные.\n',
            reply_markup=keyboard.as_markup(),
        )
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.message(Command('addnewsubscriptions'))
async def add_new_subscriptions_command(message: types.Message, state: FSMContext) -> None:
    """
    Входная точка для добавления подписок на новостные объекты себе для получения новостей

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    full_name, user_msg = message.from_user.full_name, message.text
    await add_subscriptions_body(message, full_name, user_msg, message.from_user.model_dump_json(), state)


@router.callback_query(F.data.startswith('addnewsubscriptions'))
async def add_new_subscriptions_callback(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Входная точка для добавления подписок на новостные объекты себе для получения новостей

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    user_msg = 'addnewsubscriptions'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await add_subscriptions_body(callback_query.message, full_name, user_msg, from_user.model_dump_json(), state)


@router.callback_query(SubscriptionsStates.user_subscriptions, F.data.startswith('showmeindustry'))
async def showmeindustry(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    from_user = callback_query.from_user
    chat_id, user_first_name = from_user.id, from_user.first_name
    callback_data = callback_query.data.split(':')
    show_ref_book = callback_data[1]
    if show_ref_book == 'yes':
        keyboard = InlineKeyboardBuilder()
        user_logger.info(f'Пользователь *{chat_id}* решил воспользоваться готовыми сборками подписок')
        industries = pd.read_sql_query('SELECT name FROM industry', con=engine)['name'].tolist()
        for industry in industries:
            keyboard.row(types.InlineKeyboardButton(text=industry.capitalize(), callback_data=f'whatinthisindustry:{industry}'))
        await callback_query.message.answer(
            'По какой отрасли вы бы хотели получить список клиентов и commodities?', reply_markup=keyboard.as_markup()
        )
    else:
        user_logger.info('Отмена действия - /addnewsubscriptions')
        await state.clear()
        await callback_query.message.answer('Действие успешно отменено', parse_mode='HTML', protect_content=True)


@router.callback_query(SubscriptionsStates.user_subscriptions, F.data.startswith('whatinthisindustry'))
async def whatinthisindustry(callback_query: types.CallbackQuery) -> None:
    """
    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    from_user = callback_query.from_user
    chat_id, user_first_name = from_user.id, from_user.first_name
    callback_data = callback_query.data.split(':')
    ref_book = callback_data[1]
    user_logger.info(f'Пользователь *{chat_id}* {user_first_name} смотрит список по {ref_book}')
    industry_id = pd.read_sql_query(f"SELECT id FROM industry where name = '{ref_book}'", con=engine)['id'].tolist()[0]
    clients = pd.read_sql_query(f"SELECT name FROM client where industry_id = '{industry_id}'", con=engine)
    commodity = pd.read_sql_query(f"SELECT name FROM commodity where industry_id = '{industry_id}'", con=engine)
    all_objects = pd.concat([clients, commodity], ignore_index=True)
    await callback_query.message.answer(
        handbook_format.format(ref_book.upper(), '\n'.join([name.title() for name in all_objects['name'].tolist()])),
        parse_mode='HTML',
    )
    await callback_query.message.answer(
        text='Вы можете скопировать список выше, отредактировать, если это необходимо и '
        'отправить в бота следующем сообщением, чтобы список сохранился',
    )


async def get_list_of_user_subscriptions(user_id: int) -> List[str]:
    """
    Возвращает список подписок пользователя

    :param user_id: int - telegram ID пользователя
    """
    subscriptions = pd.read_sql_query(f"SELECT subscriptions FROM whitelist WHERE user_id = '{user_id}'", con=engine)[
        'subscriptions'
    ].values.tolist()
    return subscriptions[0].split(', ') if subscriptions[0] else []


@router.message(SubscriptionsStates.user_subscriptions)
async def set_user_subscriptions(message: types.Message, state: FSMContext) -> None:
    """
    Обработка сообщения от пользователя и запись известных объектов новостей в подписки

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}: настройка пользовательских подписок')
    message_text = ''
    await state.clear()
    subscriptions = []
    quotes = ['\"', '«', '»']

    user_id = message.from_user.id

    user_subscriptions_list = await get_list_of_user_subscriptions(user_id)
    user_subscriptions_set = set(user_subscriptions_list)

    # проверяем, что у пользователя уже достигнут предел по кол-ву подписок
    if len(user_subscriptions_set) >= config.USER_SUBSCRIPTIONS_LIMIT:
        await message.reply(
            f'Достигнут предел по количеству подписок\n\n'
            f'Ваш текущий список подписок:\n\n{", ".join(user_subscriptions_set).title()}'
        )
        user_logger.info(f'*{user_id}* у пользователя уже достигнут предел по количеству подписок')

    industry_df = pd.read_sql_query('SELECT * FROM "industry_alternative"', con=engine)
    com_df = pd.read_sql_query('SELECT * FROM "client_alternative"', con=engine)
    client_df = pd.read_sql_query('SELECT * FROM "commodity_alternative"', con=engine)
    df_all = pd.concat(
        [industry_df['other_names'], client_df['other_names'], com_df['other_names']], ignore_index=True, sort=False
    ).fillna('-')
    df_all = pd.DataFrame(df_all)  # pandas.core.series.Series -> pandas.core.frame.DataFrame

    if not message_text:
        message_text = message.text

    for quote in quotes:
        message_text = message_text.replace(quote, '')
    user_request = [i.strip().lower() for i in message_text.split('\n')]

    for subscription in user_request:
        for index, row in df_all.iterrows():
            # if subscription in row.split(';') - из-за разрядности такой вариант не всегда находит совпадение
            for other_name in row['other_names'].split(';'):
                if subscription == other_name:
                    subscriptions.append(other_name)

    if len(subscriptions) < len(user_request):
        list_of_unknown = list(set(user_request) - set(subscriptions))
        ap_obj = ArticleProcess(logger=logger)
        near_to_list_of_unknown = '\n'.join(ap_obj.find_nearest_to_subjects_list(list_of_unknown))
        user_logger.debug(f'*{user_id}* Пользователь запросил неизвестные новостные ' f'объекты на подписку: {list_of_unknown}')
        reply_msg = f'{", ".join(list_of_unknown)} - Эти объекты новостей нам неизвестны'
        reply_msg += f'\n\nВозможно, вы имели в виду:\n{near_to_list_of_unknown}'
        await message.reply(reply_msg)

    if subscriptions:
        num_of_add_subscriptions = config.USER_SUBSCRIPTIONS_LIMIT - len(user_subscriptions_set)
        user_subscriptions_set.update(subscriptions[:num_of_add_subscriptions])
        not_added_subscriptions = ', '.join(subscriptions[num_of_add_subscriptions:]).title()
        subscriptions = ', '.join(user_subscriptions_set).replace("'", "''")
        with engine.connect() as conn:
            conn.execute(text(f"UPDATE whitelist SET subscriptions = '{subscriptions}' WHERE user_id = '{user_id}'"))
            conn.commit()

        msg_txt = f'Ваш новый список подписок:\n\n{subscriptions.title()}'

        if len(user_subscriptions_set) == config.USER_SUBSCRIPTIONS_LIMIT:
            msg_txt += '\n\nДостигнут предел по количеству подписок'

        if not_added_subscriptions:
            msg_txt += f'\n\nСледующие подписки не были сохранены:\n\n{not_added_subscriptions}'

        if len(msg_txt) < 4096:
            await message.reply(msg_txt)
        else:
            await message.reply('Ваши подписки были сохранены')

        user_logger.info(f'*{user_id}* Пользователь подписался на : {subscriptions.title()}')


async def get_user_subscriptions_body(message: types.Message, user_id: int) -> None:
    """
    Формирует ответное сообщение с подписками пользователя

    :param chat_id: int - ID чата с пользователем
    :param user_id: int - telegram ID пользователя
    """
    subscriptions = await get_list_of_user_subscriptions(user_id)
    chat_id = message.chat.id

    if not subscriptions:
        keyboard = types.ReplyKeyboardRemove()
        msg_txt = 'Нет активных подписок'
        user_logger.info(f'Пользователь *{chat_id}* запросил список своих подписок, но их нет')
    else:
        cancel_command = 'завершить'
        buttons = [[types.KeyboardButton(text=cancel_command)]]
        for subscription in subscriptions:
            buttons.append([types.KeyboardButton(text=subscription)])

        cancel_msg = f'Напишите «{cancel_command}» для завершения просмотра своих подписок'
        msg_txt = 'Выберите подписку\n\n' + cancel_msg
        keyboard = types.ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, input_field_placeholder=cancel_msg)
    await message.answer(msg_txt, reply_markup=keyboard)


@router.message(Command('myactivesubscriptions'))
async def get_user_subscriptions_command(message: types.Message) -> None:
    """
    Получение сообщением информации о своих подписках

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    user_id = message.from_user.id  # Get user_ID from message
    await get_user_subscriptions_body(message, user_id)


@router.callback_query(F.data.startswith('myactivesubscriptions'))
async def get_user_subscriptions_callback(callback_query: types.CallbackQuery) -> None:
    """
    Получение сообщением информации о своих подписках

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = 'myactivesubscriptions'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    user_id = from_user.id  # Get user_ID from message
    await get_user_subscriptions_body(callback_query.message, user_id)


@router.message(SubscriptionsStates.delete_user_subscriptions)
async def delete_user_subscription(message: types.Message, state: FSMContext) -> None:
    """
    Удаление своей подписки, если такая существует

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние конечного автомата
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    user_id = json.loads(message.from_user.model_dump_json())['id']  # Get user_ID from message
    subscriptions = await get_list_of_user_subscriptions(user_id)

    log_msg = f'Пользователь *{chat_id}* {full_name} запросил удаление подписки'
    keyboard = types.ReplyKeyboardRemove()
    if not subscriptions:
        msg_txt = 'Нет активных подписок'
        log_msg += ', но у пользователя нет активных подписок'
        await state.clear()
    else:
        cancel_command = 'завершить'
        cancel_msg = f'Напишите «{cancel_command}», если хотите закончить'
        msg_txt = 'Ваша подписка удалена, если хотите продолжить, напишите название следующей подписки.\n\n' + cancel_msg
        subscription_to_del = -1
        for i, subscription in enumerate(subscriptions):
            if subscription == user_msg:
                subscription_to_del = i
                break

        if subscription_to_del > -1:
            del subscriptions[subscription_to_del]
            log_msg += f' {user_msg}'

            subscriptions_update = ', '.join(subscriptions).replace("'", "''")
            with engine.connect() as conn:
                conn.execute(text(f"UPDATE whitelist SET subscriptions = '{subscriptions_update}' " f"WHERE user_id = '{user_id}'"))
                conn.commit()
        else:
            log_msg += f', но у пользователя нет подписки {user_msg}'
            msg_txt = 'Указанная подписка отсутствует\n\n' + 'Выберите подписку для удаления\n\n' + cancel_msg

        buttons = [[types.KeyboardButton(text=cancel_command)]]
        for subscription in subscriptions:
            buttons.append([types.KeyboardButton(text=subscription)])

        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True, input_field_placeholder=cancel_msg, one_time_keyboard=True
        )

    user_logger.info(log_msg)
    await message.answer(msg_txt, reply_markup=keyboard)


@router.callback_query(F.data.startswith('deletesubscriptions'))
async def delete_subscriptions(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Получение сообщением информации о своих подписках для их удаления

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние конечного автомата
    """
    chat_id = callback_query.message.chat.id
    user_msg = 'deletesubscriptions'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    user_id = from_user.id  # Get user_ID from message
    subscriptions = await get_list_of_user_subscriptions(user_id)

    log_msg = f'Пользователь *{chat_id}* {full_name} запросил список своих подписок'
    keyboard = types.ReplyKeyboardRemove()
    if not subscriptions:
        msg_txt = 'Нет активных подписок'
        log_msg += ', но их нет'
    else:
        cancel_command = 'завершить'
        await state.set_state(SubscriptionsStates.delete_user_subscriptions)
        buttons = [[types.KeyboardButton(text=cancel_command)]]
        for subscription in subscriptions:
            buttons.append([types.KeyboardButton(text=subscription)])
        cancel_msg = f'Напишите «{cancel_command}», если хотите закончить'
        msg_txt = 'Выберите подписку для удаления\n\n' + cancel_msg
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True, input_field_placeholder=cancel_msg, one_time_keyboard=True
        )

    user_logger.info(log_msg)
    await callback_query.message.answer(msg_txt, reply_markup=keyboard)


@router.callback_query(F.data.startswith('deleteallsubscriptions'))
async def delete_all_subscriptions(callback_query: types.CallbackQuery) -> None:
    """
    Получение сообщением информации о своих подписках для их удаления

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = 'deleteallsubscriptions'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    user_id = from_user.id  # Get user_ID from message
    with engine.connect() as conn:
        conn.execute(text(f"UPDATE whitelist SET subscriptions = '' WHERE user_id = '{user_id}'"))
        conn.commit()

    msg_txt = 'Подписки удалены'
    await callback_query.message.answer(msg_txt, reply_markup=types.ReplyKeyboardRemove())


@router.message(Command('subscriptions_menu'))
async def subscriptions_menu(message: types.Message) -> None:
    """
    Получение меню для взаимодействия с подписками

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text='Список активных подписок', callback_data='myactivesubscriptions'))
        keyboard.row(types.InlineKeyboardButton(text='Добавить новые подписки', callback_data='addnewsubscriptions'))
        keyboard.row(types.InlineKeyboardButton(text='Удалить подписки', callback_data='deletesubscriptions'))
        keyboard.row(types.InlineKeyboardButton(text='Удалить все подписки', callback_data='deleteallsubscriptions'))

        await message.answer(text='Меню управления подписками\n', reply_markup=keyboard.as_markup())
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(UserTGSubs.filter())
async def get_my_tg_subscriptions(callback_query: types.CallbackQuery, callback_data: UserTGSubs) -> None:
    """
    Изменяет сообщение, отображая информацию о подписках на тг каналы пользователя

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о текущей странице, id удаляемой подписки (0 - не удаляем)
    """
    chat_id = callback_query.message.chat.id
    user_msg = USER_TG_SUBS
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    page = callback_data.page
    delete_tg_sub_id = callback_data.delete_tg_sub_id

    if delete_tg_sub_id:
        delete_user_telegram_subscription(user_id, delete_tg_sub_id)

    user_tg_subs_df = get_user_tg_subscriptions_df(user_id)
    page_data, page_info, max_pages = get_page_data_and_info(user_tg_subs_df, page)
    msg_text = (
        f'Ваш список подписок на telegram каналы\n<b>{page_info}</b>\n'
        f'Для получения более детальной информации о канале - нажмите на него\n\n'
        f'Для удаления канала из подписок - нажмите на "{DELETE_CROSS}" рядом с каналом'
    )
    keyboard = kb_maker.get_tg_subs_watch_kb(page_data, page, max_pages)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def show_tg_channel_more_info(
        callback_query: types.CallbackQuery, telegram_id: int, is_subscribed: bool, back: str, user_msg: str
) -> None:
    """"""
    chat_id = callback_query.message.chat.id
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    telegram_channel_info = get_telegram_channel_info(telegram_id)

    msg_text = (
        f'Название: <b>{telegram_channel_info["name"]}</b>\n'
        # f'Description: {}\n'
        f'Ссылка: {telegram_channel_info["link"]}\n'
        f'Отрасль: <b>{telegram_channel_info["industry_name"]}</b>\n'
    )
    keyboard = get_tg_info_kb(telegram_id, is_subscribed, back)

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML')
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(TGSubAction.filter())
async def update_sub_on_tg_channel(callback_query: types.CallbackQuery, callback_data: TGSubAction) -> None:
    """
    Предоставляет инфу о тг канале

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с telegram_id
    """
    telegram_id = callback_data.telegram_id
    need_add = callback_data.need_add
    user_id = callback_query.from_user.id

    if need_add:
        # add sub
        add_user_telegram_subscription(user_id, telegram_id)
    else:
        # delete sub on tg channel
        delete_user_telegram_subscription(user_id, telegram_id)

    await show_tg_channel_more_info(callback_query, telegram_id, need_add, callback_data.back, TG_SUB_ACTION)


@router.callback_query(TGChannelMoreInfo.filter())
async def get_tg_channel_more_info(callback_query: types.CallbackQuery, callback_data: TGChannelMoreInfo) -> None:
    """
    Предоставляет инфу о тг канале

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с telegram_id
    """
    await show_tg_channel_more_info(
        callback_query, callback_data.telegram_id, callback_data.is_subscribed, callback_data.back, TG_CHANNEL_INFO
    )


@router.callback_query(IndustryTGChannels.filter())
async def get_industry_tg_channels(callback_query: types.CallbackQuery, callback_data: IndustryTGChannels) -> None:
    """
    Предоставляет подборку тг каналов по отрасли

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с industry_id
    """
    chat_id = callback_query.message.chat.id
    user_msg = TG_SUBS_DELETE_ALL_DONE
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    industry_id = callback_data.industry_id
    telegram_id = callback_data.telegram_id
    need_add = callback_data.need_add

    if telegram_id:
        if need_add:
            add_user_telegram_subscription(user_id, telegram_id)
        else:
            delete_user_telegram_subscription(user_id, telegram_id)

    industry_name = get_industry_name(industry_id)
    tg_channel_df = get_industry_tg_channels_df(industry_id, user_id)
    msg_text = (
        f'Подборка telegram каналов по отрасли "{industry_name}"\n\n'
        f'Для добавления/удаления подписки на telegram канала нажмите на {UNSELECTED}/{SELECTED} соответственно\n\n'
        f'Для получения более детальной информации о канале - нажмите на него'
    )
    keyboard = kb_maker.get_industry_tg_channels_kb(industry_id, tg_channel_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(TG_SUBS_INDUSTRIES_MENU))
async def get_tg_subs_industries_menu(callback_query: types.CallbackQuery) -> None:
    """
    Отображает список отраслей, которые связаны с какими-либо telegram каналами

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = TG_SUBS_INDUSTRIES_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    industry_df = get_industries()
    msg_text = 'Выберите подборку telegram каналов по отраслям'
    keyboard = kb_maker.get_tg_subs_industries_menu_kb(industry_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(TG_SUBS_DELETE_ALL_DONE))
async def delete_all_tg_subs_done(callback_query: types.CallbackQuery) -> None:
    """
    Удаляет подписки пользователя на тг каналы
    Уведомляет пользователя, что удаление всех подписок завершено

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = TG_SUBS_DELETE_ALL_DONE
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    delete_all_user_telegram_subscriptions(user_id)

    msg_text = 'Ваши подписки на telegram каналы были удалены'
    keyboard = kb_maker.get_back_to_tg_subs_menu_kb()
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(TG_SUBS_DELETE_ALL))
async def delete_all_tg_subs(callback_query: types.CallbackQuery) -> None:
    """
    Подтвреждение действия

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = TG_SUBS_DELETE_ALL
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = callback_query.from_user.id

    user_tg_subs = get_user_tg_subscriptions_df(user_id=user_id)

    if user_tg_subs.empty:
        msg_text = 'У вас отсутствуют подписки'
        keyboard = kb_maker.get_back_to_tg_subs_menu_kb()
    else:
        msg_text = 'Вы уверены, что хотите удалить все подписки на telegram каналы?'
        keyboard = kb_maker.get_prepare_tg_subs_delete_all_kb()

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def tg_subs_menu(message: Union[types.CallbackQuery, types.Message]) -> None:
    keyboard = kb_maker.get_tg_subscriptions_menu_kb()
    msg_text = (
        'Меню управления подписками на telegram каналы\n\n'
        'На основе ваших подписок формируется сводка новостей по отрасли, с которой связаны telegram каналы'
    )

    # Проверяем, что за тип апдейта. Если Message - отправляем новое сообщение
    if isinstance(message, types.Message):
        await message.answer(msg_text, reply_markup=keyboard)

    # Если CallbackQuery - изменяем это сообщение
    else:
        call = message
        await call.message.edit_text(msg_text, reply_markup=keyboard)


@router.callback_query(F.data.startswith(BACK_TO_MENU))
async def back_to_tg_subs_menu(callback_query: types.CallbackQuery) -> None:
    """
    Фозвращает пользователя в меню (меняет сообщение, с которым связан колбэк)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = BACK_TO_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await tg_subs_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command('tg_subscriptions_menu'))
async def tg_subscriptions_menu(message: types.Message) -> None:
    """
    Получение меню для взаимодействия с подписками на telegram каналы (влияет на сводку новостей по отрасли)

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        await tg_subs_menu(message)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')
