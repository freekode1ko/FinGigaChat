import copy
import json
import math
from typing import List, Union

import pandas as pd
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import text

from configs import config
from log.bot_logger import logger, user_logger
from constants.bot import subscriptions as callback_prefixes
from constants.constants import handbook_prefix, DELETE_CROSS, UNSELECTED, SELECTED
from database import engine
from keyboards.subscriptions.callbacks import (
    UserTGSubs,
    TGChannelMoreInfo,
    IndustryTGChannels,
    TGSubAction,
    AddAllSubsByDomain,
)
from keyboards.subscriptions import constructors as kb_maker
from keyboards.subscriptions.constructors import get_tg_info_kb
from module.article_process import ArticleProcess
from utils.base import user_in_whitelist, get_page_data_and_info, bot_send_msg, send_or_edit
from utils.industry import get_industries_with_tg_channels, get_industry_name
from utils.subscriptions import (
    get_user_tg_subscriptions_df,
    delete_user_telegram_subscription,
    delete_all_user_telegram_subscriptions,
    get_industry_tg_channels_df,
    get_telegram_channel_info,
    add_user_telegram_subscription,
)

emoji = copy.deepcopy(config.dict_of_emoji)

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


class SubscriptionsStates(StatesGroup):
    user_subscriptions = State()
    delete_user_subscriptions = State()


@router.callback_query(F.data.startswith('addnewsubscriptions'))
async def select_or_write(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Напишу сам/Справочник по подпискам', callback_data='writesubs'))
    keyboard.row(types.InlineKeyboardButton(text='Выберу из меню/Подписка на отрасль', callback_data='selectsubs'))
    keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data='end_write_subs'))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_prefixes.SUBS_MENU))
    await state.clear()

    await callback_query.message.edit_text('Как вы хотите заполнить подписки?', reply_markup=keyboard.as_markup())


@router.callback_query(F.data.startswith('writesubs'))
async def write_new_subscriptions_callback(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Формирует ответное сообщение для добавления подписок

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    user_msg = 'writesubs'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    chat_id = from_user.id

    if await user_in_whitelist(from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await state.set_state(SubscriptionsStates.user_subscriptions)
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text='Показать готовые подборки', callback_data='showmeindustry:yes'))
        keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data='end_write_subs'))
        keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data='addnewsubscriptions'))
        await callback_query.message.edit_text(
            'Сформируйте полный список интересующих клиентов и/или commodities, и/или отрасли '
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


@router.callback_query(AddAllSubsByDomain.filter())
async def add_all_subs(callback_query: types.CallbackQuery, callback_data: AddAllSubsByDomain) -> None:
    """
    Подписывает пользователя на все подписки из области

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Содержит информацию о выбранной области
    """
    table_name = callback_data.domain

    user_subscriptions = await get_list_of_user_subscriptions(callback_query.from_user.id)
    user_subscriptions_uniq = set(user_subscriptions)
    if not await is_subscription_limit_reached(callback_query.message, user_subscriptions_uniq):
        sub_element = pd.read_sql_query(f'SELECT name FROM {table_name}', con=engine)
        elements_to_add = list(set(i[0] for i in sub_element.values.tolist()) - user_subscriptions_uniq)
        subs_count = len(user_subscriptions)

        if elements_to_add:
            num_of_add_subscriptions = config.USER_SUBSCRIPTIONS_LIMIT - subs_count
            new_subs = elements_to_add[:num_of_add_subscriptions]
            user_subscriptions.extend(new_subs)
            user_subscriptions.sort()
            new_user_subscription_str = ', '.join(user_subscriptions).replace("'", "''")
            new_subs = ', '.join(new_subs).title()

            with engine.connect() as conn:
                sql_text = f"UPDATE whitelist set subscriptions = '{new_user_subscription_str}' WHERE user_id = {callback_query.from_user.id}"
                conn.execute(text(sql_text))
                conn.commit()

            # Здесь "отрасли" это костыль
            msg_text = (
                f'{new_subs} - добавлены к вашим подпискам\n'
                f'Можете подписаться еще на дополнительные отрасли '
                f'или выбрать другой раздел'
            )
        else:
            msg_text = 'Вы уже подписаны на все отрасли\nВыберите другой раздел'

        await callback_query.message.answer(msg_text)


@router.callback_query(F.data.startswith('addsub'))
async def append_new_subscription(callback_query: types.CallbackQuery = None) -> None:
    element_id, table_name = callback_query.data.split(':')[2], callback_query.data.split(':')[1]
    user_subscriptions = await get_list_of_user_subscriptions(callback_query.from_user.id)
    user_subscriptions_uniq = set(user_subscriptions)
    if not await is_subscription_limit_reached(callback_query.message, user_subscriptions_uniq):
        sub_element = pd.read_sql_query(f'SELECT name FROM {table_name} WHERE id = {element_id}', con=engine)
        element_to_add = sub_element.values.tolist()[0][0]
        subs_count = len(user_subscriptions)

        user_subscriptions.append(element_to_add)
        new_user_subscription = list(set(user_subscriptions))
        new_user_subscription.sort()
        new_user_subscription_str = ', '.join(new_user_subscription).replace("'", "''")

        with engine.connect() as conn:
            sql_text = f"UPDATE whitelist set subscriptions = '{new_user_subscription_str}' WHERE user_id = {callback_query.from_user.id}"
            conn.execute(text(sql_text))
            conn.commit()

        if subs_count < len(new_user_subscription):
            await callback_query.message.answer(
                f'{element_to_add.capitalize()} - добавлен к вашим подпискам\n'
                f'Можете подписаться еще на дополнительные отрасли '
                f'или выбрать другой раздел',
            )
        else:
            await callback_query.message.answer(
                f'{element_to_add.capitalize()} - уже есть в ваших подписках\n'
                f'Можете подписаться еще на дополнительные отрасли '
                f'или выбрать другой раздел',
            )


async def pagination(pages, search, cur_page: int = 0, first_button: types.InlineKeyboardButton = None) -> types.InlineKeyboardMarkup:
    buttons = []
    if first_button is not None:
        buttons.append([first_button])
    for element in pages[cur_page].values.tolist():
        buttons.append([types.InlineKeyboardButton(text=f'{element[1].capitalize()}', callback_data=f'addsub:{search}:{element[0]}')])
    bottom_buttons = []
    if cur_page != 0:
        callback = f'page:back:{cur_page}:{search}'
        bottom_buttons.append(types.InlineKeyboardButton(text=emoji['backward'], callback_data=callback))
    else:
        bottom_buttons.append(types.InlineKeyboardButton(text=emoji['block'], callback_data='stop'))

    bottom_buttons.append(types.InlineKeyboardButton(text=f'{cur_page + 1}/{len(pages)}', callback_data='pagination'))

    if cur_page == len(pages) - 1:
        bottom_buttons.append(types.InlineKeyboardButton(text=emoji['block'], callback_data='stop'))
    else:
        callback = f'page:forward:{cur_page}:{search}'
        bottom_buttons.append(types.InlineKeyboardButton(text=emoji['forward'], callback_data=callback))

    buttons.append(bottom_buttons)
    buttons.append([types.InlineKeyboardButton(text='Завершить', callback_data='end_write_subs')])
    buttons.append([types.InlineKeyboardButton(text='Назад к выбору раздела', callback_data='selectsubs')])
    keyboard = types.InlineKeyboardMarkup(row_width=1, inline_keyboard=buttons)
    return keyboard


@router.callback_query(F.data.startswith('page'))
async def scroller(query: types.CallbackQuery = None) -> None:
    input_params = query.data.split(':')
    direction = input_params[1]
    cur_page = int(input_params[2])
    search = input_params[3]
    table_ru_names = {
        'client': {
            'domain': 'Клиенты',
            'first_button': None,
        },
        'commodity': {
            'domain': 'Сырьевые товары',
            'first_button': None,
        },
        'industry': {
            'domain': 'Отрасли',
            'first_button': types.InlineKeyboardButton(
                text='Подписаться на все',
                callback_data=AddAllSubsByDomain(domain='industry').pack(),
            ),
        },
    }

    try:
        table = pd.read_sql_query(f'SELECT id, name FROM {search}', con=engine)
    except Exception as e:
        table = pd.DataFrame(columns=['id', 'name'])

    page_elements_cnt = 10
    chunks = []
    num_chunks = math.ceil(len(table) / page_elements_cnt)
    for index in range(num_chunks):
        chunks.append(table[index * page_elements_cnt: (index + 1) * page_elements_cnt])

    search_data = table_ru_names.get(search, {})
    domain = search_data.get('domain', 'Ошибка')
    first_button = search_data.get('first_button')
    cur_page += 1 if direction == 'forward' else -1
    keyboard = await pagination(chunks, search, cur_page, first_button)
    await query.message.edit_text(text=f'{domain}\nСтраница {cur_page+1} из {len(chunks)}', reply_markup=keyboard)


@router.callback_query(F.data.startswith('selectsubs'))
async def select_subs_from_menu(callback_query: types.CallbackQuery = None) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(types.InlineKeyboardButton(text='Клиенты', callback_data='page:empty:1:client'))
    keyboard.row(types.InlineKeyboardButton(text='Сырьевые товары', callback_data='page:empty:1:commodity'))
    keyboard.row(types.InlineKeyboardButton(text='Отрасли', callback_data='page:empty:1:industry'))
    keyboard.row(types.InlineKeyboardButton(text='Завершить', callback_data='end_write_subs'))
    keyboard.row(types.InlineKeyboardButton(text='Назад', callback_data='addnewsubscriptions'))

    await callback_query.message.edit_text(text='Выберете раздел', reply_markup=keyboard.as_markup())


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
    all_objects = pd.concat([clients, commodity], ignore_index=True)['name'].tolist()

    await bot_send_msg(
        callback_query.message.bot,
        chat_id,
        '\n'.join([name.title() for name in all_objects]),
        delimiter='\n',
        prefix=handbook_prefix.format(ref_book.upper()),
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


async def is_subscription_limit_reached(message: types.Message, user_subscriptions_set) -> bool:
    # проверяем, что у пользователя уже достигнут предел по кол-ву подписок
    if len(user_subscriptions_set) >= config.USER_SUBSCRIPTIONS_LIMIT:
        user_id = message.from_user.id
        await message.answer(
            f'Достигнут предел по количеству подписок\n\n'
            f'Ваш текущий список подписок:\n\n{", ".join(user_subscriptions_set).title()}'
        )
        user_logger.info(f'*{user_id}* у пользователя уже достигнут предел по количеству подписок')
        return True
    return False


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
    subscriptions = []
    quotes = ['\"', '«', '»']

    user_id = message.from_user.id

    user_subscriptions_list = await get_list_of_user_subscriptions(user_id)
    user_subscriptions_set = set(user_subscriptions_list)

    # проверяем, что у пользователя уже достигнут предел по кол-ву подписок
    if await is_subscription_limit_reached(message, user_subscriptions_set):
        await state.clear()
        return

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

    continue_keyboard = InlineKeyboardBuilder()
    continue_keyboard.add(types.InlineKeyboardButton(text='Завершить', callback_data='end_write_subs'))
    continue_keyboard = continue_keyboard.as_markup()
    continue_msg = '\n\nЕсли хотите завершить формирование подписок, то нажмите кнопку "Завершить"'

    if len(subscriptions) < len(user_request):
        list_of_unknown = list(set(user_request) - set(subscriptions))
        ap_obj = ArticleProcess(logger=logger)
        near_to_list_of_unknown = '\n'.join(ap_obj.find_nearest_to_subjects_list(list_of_unknown))
        user_logger.info(f'*{user_id}* Пользователь запросил неизвестные новостные ' f'объекты на подписку: {list_of_unknown}')
        reply_msg = f'{", ".join(list_of_unknown)} - Эти объекты новостей нам неизвестны'
        reply_msg += f'\n\nВозможно, вы имели в виду:\n{near_to_list_of_unknown}'
        # Если нет корректных названий, то новых подписок не добавляем и предлагаем пользователю продолжить формирование
        # Иначе предлагаем продолжить в сообщении об успешном добавлении новых подписок
        keyboard = None
        if len(subscriptions) == 0:
            keyboard = continue_keyboard
            reply_msg += continue_msg
        await message.reply(reply_msg, reply_markup=keyboard)

    # Если есть новые подписки, которые можем добавить
    if subscriptions:
        num_of_add_subscriptions = config.USER_SUBSCRIPTIONS_LIMIT - len(user_subscriptions_set)
        new_subs = subscriptions[:num_of_add_subscriptions]
        user_subscriptions_set.update(new_subs)
        not_added_subscriptions = ', '.join(subscriptions[num_of_add_subscriptions:]).title()
        new_subs = ', '.join(new_subs).title()
        subscriptions = ', '.join(user_subscriptions_set).replace("'", "''")
        with engine.connect() as conn:
            conn.execute(text(f"UPDATE whitelist SET subscriptions = '{subscriptions}' WHERE user_id = '{user_id}'"))
            conn.commit()

        user_logger.info(f'*{user_id}* Пользователь подписался на : {new_subs}')

        keyboard = continue_keyboard
        msg_txt = f'Ваш список подписок:\n\n{subscriptions.title()}'
        limit_msg = ''
        unsaved_subs_msg = ''

        if len(user_subscriptions_set) == config.USER_SUBSCRIPTIONS_LIMIT:
            keyboard = None
            continue_msg = ''
            limit_msg = '\n\nДостигнут предел по количеству подписок'
            await state.clear()

        if not_added_subscriptions:
            unsaved_subs_msg = f'\n\nСледующие подписки не были сохранены:\n\n{not_added_subscriptions}'

        if len(msg_txt) + len(limit_msg) + len(unsaved_subs_msg) + len(continue_msg) > 4096:
            msg_txt = 'Ваши подписки были сохранены'

        msg_txt += limit_msg + unsaved_subs_msg + continue_msg

        await message.reply(msg_txt, reply_markup=keyboard)


@router.callback_query(F.data.startswith('continue_write_subs'))
async def continue_write_subs(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SubscriptionsStates.user_subscriptions)
    await callback_query.message.edit_reply_markup()
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Завершить', callback_data='end_write_subs'))
    await callback_query.message.answer(text='Продолжайте вводить подписки', reply_markup=keyboard.as_markup())


@router.callback_query(F.data.startswith('end_write_subs'))
async def end_write_subs(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.answer(text='Формирование подписок завершено')


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

    subscriptions = await get_list_of_user_subscriptions(user_id)

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
    await callback_query.message.answer(msg_txt, reply_markup=keyboard)


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


@router.callback_query(F.data.startswith(callback_prefixes.SUBS_DELETE_ALL_DONE))
async def delete_all_subscriptions(callback_query: types.CallbackQuery) -> None:
    """
    Получение сообщением информации о своих подписках для их удаления

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.SUBS_DELETE_ALL_DONE
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    user_id = from_user.id  # Get user_ID from message
    with engine.connect() as conn:
        conn.execute(text(f"UPDATE whitelist SET subscriptions = '' WHERE user_id = '{user_id}'"))
        conn.commit()

    msg_txt = 'Подписки удалены'
    keyboard = kb_maker.get_back_to_subs_menu_kb()
    await callback_query.message.edit_text(text=msg_txt, reply_markup=keyboard)


@router.callback_query(F.data.startswith('deleteallsubscriptions'))
async def delete_all_subscriptions(callback_query: types.CallbackQuery) -> None:
    """
    Подтвреждение действия

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = 'deleteallsubscriptions'
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    user_id = callback_query.from_user.id

    user_subs = await get_list_of_user_subscriptions(user_id=user_id)

    if not user_subs:
        msg_text = 'У вас отсутствуют подписки'
        keyboard = kb_maker.get_back_to_subs_menu_kb()
    else:
        msg_text = 'Вы уверены, что хотите удалить все подписки?'
        keyboard = kb_maker.get_prepare_subs_delete_all_kb()

    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


async def subs_menu(message: Union[types.CallbackQuery, types.Message]) -> None:
    """Формирует меню подписок"""
    keyboard = kb_maker.get_subscriptions_kb()
    msg_text = 'Меню управления подписками\n'
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(F.data.startswith(callback_prefixes.SUBS_MENU))
async def subscriptions_menu_callback(callback_query: types.CallbackQuery) -> None:
    """
    Получение меню для взаимодействия с подписками

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.SUBS_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    await subs_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.message(Command(callback_prefixes.SUBS_MENU))
async def subscriptions_menu(message: types.Message) -> None:
    """
    Получение меню для взаимодействия с подписками

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await subs_menu(message)
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
    user_msg = callback_prefixes.USER_TG_SUBS
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

    await show_tg_channel_more_info(
        callback_query, telegram_id, need_add, callback_data.back, callback_prefixes.TG_SUB_ACTION
    )


@router.callback_query(TGChannelMoreInfo.filter())
async def get_tg_channel_more_info(callback_query: types.CallbackQuery, callback_data: TGChannelMoreInfo) -> None:
    """
    Предоставляет инфу о тг канале

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с telegram_id
    """
    await show_tg_channel_more_info(
        callback_query,
        callback_data.telegram_id,
        callback_data.is_subscribed,
        callback_data.back,
        callback_prefixes.TG_CHANNEL_INFO,
    )


@router.callback_query(IndustryTGChannels.filter())
async def get_industry_tg_channels(callback_query: types.CallbackQuery, callback_data: IndustryTGChannels) -> None:
    """
    Предоставляет подборку тг каналов по отрасли

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Хранит атрибут с industry_id
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.INDUSTRY_TG_CHANNELS
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


@router.callback_query(F.data.startswith(callback_prefixes.TG_SUBS_INDUSTRIES_MENU))
async def get_tg_subs_industries_menu(callback_query: types.CallbackQuery) -> None:
    """
    Отображает список отраслей, которые связаны с какими-либо telegram каналами

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.TG_SUBS_INDUSTRIES_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    industry_df = get_industries_with_tg_channels()
    msg_text = 'Выберите подборку telegram каналов по отраслям'
    keyboard = kb_maker.get_tg_subs_industries_menu_kb(industry_df)
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.TG_SUBS_DELETE_ALL_DONE))
async def delete_all_tg_subs_done(callback_query: types.CallbackQuery) -> None:
    """
    Удаляет подписки пользователя на тг каналы
    Уведомляет пользователя, что удаление всех подписок завершено

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.TG_SUBS_DELETE_ALL_DONE
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_id = callback_query.from_user.id
    delete_all_user_telegram_subscriptions(user_id)

    msg_text = 'Ваши подписки на telegram каналы были удалены'
    keyboard = kb_maker.get_back_to_tg_subs_menu_kb()
    await callback_query.message.edit_text(msg_text, reply_markup=keyboard)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.TG_SUBS_DELETE_ALL))
async def delete_all_tg_subs(callback_query: types.CallbackQuery) -> None:
    """
    Подтвреждение действия

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.TG_SUBS_DELETE_ALL
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


@router.callback_query(F.data.startswith(callback_prefixes.TG_END_WRITE_SUBS))
async def tg_end_write_subs(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню подписок на тг каналы

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние конечного автомата
    """
    await state.clear()
    await callback_query.message.edit_text(text='Формирование подписок завершено')


async def tg_subs_menu(message: Union[types.CallbackQuery, types.Message]) -> None:
    keyboard = kb_maker.get_tg_subscriptions_menu_kb()
    msg_text = (
        'Меню управления подписками на telegram каналы\n\n'
        'На основе ваших подписок формируется сводка новостей по отрасли, с которой связаны telegram каналы'
    )
    await send_or_edit(message, msg_text, keyboard)


@router.callback_query(F.data.startswith(callback_prefixes.BACK_TO_TG_MENU))
async def back_to_tg_subs_menu(callback_query: types.CallbackQuery) -> None:
    """
    Фозвращает пользователя в меню (меняет сообщение, с которым связан колбэк)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = callback_prefixes.BACK_TO_TG_MENU
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