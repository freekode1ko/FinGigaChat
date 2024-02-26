import json
# import logging
from typing import Union, List

import pandas as pd
from aiogram import F, Router, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
import database
from bot_logger import logger, user_logger
from constants.bot.admin import BACK_TO_DELETE_NEWSLETTER_MSG_MENU
from database import engine
from keyboards.admin.callbacks import DeleteMessageByType, ApproveDeleteMessageByType
import keyboards.admin.constructors as kb_maker
from module.article_process import ArticleProcessAdmin
from module.model_pipe import summarization_by_chatgpt
from utils.bot.base import (
    is_admin_user,
    file_cleaner,
    send_msg_to,
    user_in_whitelist,
)
from utils.bot.newsletter import subscriptions_newsletter
from utils.db_api.message import get_messages_by_type, delete_messages, add_all
from utils.db_api.message_type import message_types

TG_DELETE_MESSAGE_IDS_LEN_LIMIT = 100

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


class AdminStates(StatesGroup):
    link = State()
    link_change_summary = State()
    link_to_delete = State()
    send_to_users = State()


@router.message(Command('sendtoall'))
async def message_to_all(message: types.Message, state: FSMContext) -> None:
    """
    Входная точка для ручной рассылки новостей на всех пользователей

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    user_str = message.from_user.model_dump_json()
    user = json.loads(message.from_user.model_dump_json())
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if await user_in_whitelist(user_str):
        if await is_admin_user(user):
            await state.set_state(AdminStates.send_to_users)
            await message.answer(
                'Сформируйте сообщение для всех пользователей в следующем своем сообщении\n'
                'или, если передумали, напишите слово "Отмена".'
            )
            user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        else:
            await message.answer('Недостаточно прав для этой команды!')
            user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')
    else:
        await message.answer('Неавторизованный пользователь')
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.message(AdminStates.send_to_users, F.content_type.in_({'text', 'document', 'photo'}))
async def get_msg_from_admin(message: types.Message, state: FSMContext) -> None:
    """
    Обработка сообщения и/или файла от пользователя и рассылка их на всех пользователей

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    """
    message_jsn = json.loads(message.model_dump_json())
    if message.content_type == types.ContentType.TEXT:
        file_type = 'text'
        file_name = None
        msg = message.text
    elif message.content_type == types.ContentType.DOCUMENT:
        file_type = 'document'
        file_name = message.document.file_name
        msg = message.caption
        await message.bot.download(message.document, destination=f'sources/{file_name}')
    elif message.content_type == types.ContentType.PHOTO:
        file_type = 'photo'
        best_photo = message.photo[0]
        for photo_file in message.photo[1:]:
            if best_photo.file_size < photo_file.file_size:
                best_photo = photo_file
        file_name = best_photo.file_id
        await message.bot.download(best_photo, destination=f'sources/{file_name}.jpg')
        msg = message.caption
    else:
        await state.clear()
        await message.answer('Отправка не удалась')
        return None

    await state.clear()
    users = pd.read_sql_query('SELECT * FROM whitelist', con=engine)
    users_ids = users['user_id'].tolist()
    saved_messages: List[dict] = []
    newsletter_type = 'default'
    successful_sending = 0
    for user_id in users_ids:
        try:
            user_logger.debug(f'*{user_id}* Отправка пользователю сообщения от админа')
            m = await send_msg_to(message.bot, user_id, msg, file_name, file_type)
            saved_messages.append(dict(user_id=user_id, message_id=m.message_id, message_type=newsletter_type))
            user_logger.debug(f'*{user_id}* Пользователю пришло сообщение {m.message_id} от админа')
            successful_sending += 1
        # except BotBlocked:
        #     user_logger.warning(f'*{user_id}* Пользователь поместил бота в блок, он не получил сообщения')
        except Exception as ex:
            user_logger.error(f'*{user_id}* Пользователь не получил сообщения из-за ошибки: {ex}')

    add_all(saved_messages)
    await message.answer('Рассылка отправлена для {} из {} пользователей'.format(successful_sending, len(users_ids)))
    logger.info('Рассылка отправлена для {} из {} пользователей'.format(successful_sending, len(users_ids)))

    file_cleaner('sources/{}'.format(file_name))
    file_cleaner('sources/{}.jpg'.format(file_name))


@router.message(Command('admin_help'))
async def admin_help(message: types.Message) -> None:
    """
    Вывод в чат подсказки по командам для администратора

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user = json.loads(message.from_user.model_dump_json())
    admin_flag = await is_admin_user(user)

    if admin_flag:
        # TODO: '<b>/analyse_bad_article</b> - показать возможные нерелевантные новости\n'
        help_msg = (
            '<b>/show_article</b> - показать детальную информацию о новости\n'
            '<b>/change_summary</b> - поменять саммари новости с помощью LLM\n'
            '<b>/delete_article</b> - удалить новость из базы данных\n'
            '<b>/sendtoall</b> - отправить сообщение на всех пользователей'
        )
        await message.answer(help_msg, protect_content=False, parse_mode='HTML')
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=False)
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')


@router.message(Command('show_article'))
async def show_article(message: types.Message, state: FSMContext) -> None:
    """
    Вывод в чат новости по ссылке

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    user = json.loads(message.from_user.model_dump_json())
    admin_flag = await is_admin_user(user)

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите получить.'
        await state.set_state(AdminStates.link)
        await message.bot.send_message(
            chat_id=message.chat.id, text=ask_link, parse_mode='HTML', protect_content=False, disable_web_page_preview=True
        )
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=False)
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')


@router.message(AdminStates.link)
async def continue_show_article(message: types.Message, state: FSMContext) -> None:
    """
    Вывод новости по ссылке от пользователя

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    """
    await state.update_data(link=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    article_id = apd_obj.get_article_id_by_link(data['link'])
    if not article_id:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.', protect_content=False)
        await state.clear()
        user_logger.warning(f"/show_article : не получилось найти новость по ссылке '{data['link']}'")
        return

    data_article_dict = apd_obj.get_article_by_link(data['link'])
    if not isinstance(data_article_dict, dict):
        await message.answer(f'Извините, произошла ошибка: {data_article_dict}.\nПопробуйте в другой раз.', protect_content=False)
        user_logger.critical(f'/show_article : {data_article_dict}')
        return

    format_msg = ''
    for key, val in data_article_dict.items():
        format_msg += f'<b>{key}</b>: {val}\n'

    await message.answer(format_msg, parse_mode='HTML', protect_content=False, disable_web_page_preview=True)
    await state.clear()


@router.message(Command('change_summary'))
async def change_summary(message: types.Message, state: FSMContext) -> None:
    """
    Получение ссылки на новость для изменения ее короткой версии

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if not config.api_key_gpt:
        await message.answer('Данная команда пока недоступна.', protect_content=False)
        user_logger.critical('Нет токена доступа к chatGPT')
        return

    user = json.loads(message.from_user.model_dump_json())
    admin_flag = await is_admin_user(user)

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите изменить.'
        await state.set_state(AdminStates.link_change_summary)
        await message.bot.send_message(
            chat_id=message.chat.id, text=ask_link, parse_mode='HTML', protect_content=False, disable_web_page_preview=True
        )
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.', protect_content=False)
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')


@router.message(AdminStates.link_change_summary)
async def continue_change_summary(message: types.Message, state: FSMContext) -> None:
    """
    Изменение краткой версии новости

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    """
    await state.update_data(link_change_summary=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    full_text, old_text_sum = apd_obj.get_article_text_by_link(data['link_change_summary'])

    if not full_text:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.', protect_content=False)
        await state.clear()
        user_logger.warning(f"/change_summary : не получилось найти новость по ссылке - {data['link_change_summary']}")
        return

    await message.answer('Создание саммари может занять некоторое время. Ожидайте.', protect_content=False)

    try:
        new_text_sum = summarization_by_chatgpt(full_text)
        apd_obj.insert_new_gpt_summary(new_text_sum, data['link_change_summary'])
        await message.answer(f'<b>Старое саммари:</b> {old_text_sum}', parse_mode='HTML', protect_content=False)

    # except MessageIsTooLong:
    #     await message.answer('<b>Старое саммари не помещается в одно сообщение.</b>', parse_mode='HTML')
    #     user_logger.critical(
    #         f'/change_summary : старое саммари оказалось слишком длинным ' f"({data['link_change_summary']}\n{old_text_sum})"
    #     )

    except Exception:
        user_logger.critical('/change_summary : ошибка при создании саммари с помощью chatGPT')
        await message.answer('Произошла ошибка при создании саммари. Разработчики уже решают проблему.', protect_content=False)

    else:
        await message.answer(f'<b>Новое саммари:</b> {new_text_sum}', parse_mode='HTML', protect_content=False)
        await state.clear()


@router.message(Command('delete_article'))
async def delete_article(message: types.Message, state: FSMContext) -> None:
    """
    Получение ссылки на новость от пользователя для ее удаления (снижения значимости)

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Объект, который хранит состояние FSM для пользователя
    """
    user = json.loads(message.from_user.model_dump_json())
    admin_flag = await is_admin_user(user)
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if admin_flag:
        ask_link = 'Вставьте ссылку на новость, которую хотите удалить.'
        await state.set_state(AdminStates.link_to_delete)
        await message.answer(text=ask_link, parse_mode='HTML', disable_web_page_preview=True)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.')
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')


@router.message(AdminStates.link_to_delete)
async def continue_delete_article(message: types.Message, state: FSMContext) -> None:
    """
    Проверка, что действие по удалению новости не случайное и выбор причины удаления (снижения значимости)
    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: конечный автомат о состоянии
    """
    await state.update_data(link_to_delete=message.text)
    data = await state.get_data()

    apd_obj = ArticleProcessAdmin()
    article_id = apd_obj.get_article_id_by_link(data['link_to_delete'])
    if not article_id:
        await message.answer('Извините, не могу найти новость. Попробуйте в другой раз.')
        await state.clear()
        user_logger.warning(f"/delete_article : не получилось найти новость по ссылке - {data['link_to_delete']}")
        return
    else:
        del_buttons_data_dict = dict(
            cancel='Отменить удаление',
            duplicate='Удалить дубль',
            useless='Удалить незначимую новость',
            not_relevant='Удалить нерелевантную новость',
            another='Удалить по другой причине',
        )
        callback_func = 'end_del_article'
        keyboard = InlineKeyboardBuilder()

        for reason, label in del_buttons_data_dict.items():
            callback = f'{callback_func}:{reason}:{article_id}'  # макс. длина 64 символа
            keyboard.row(types.InlineKeyboardButton(text=label, callback_data=callback))

        await message.answer('Выберите причину удаления новости:', reply_markup=keyboard.as_markup())
        await state.clear()


@router.callback_query(F.data.startswith('end_del_article'))
async def end_del_article(callback_query: types.CallbackQuery) -> None:
    """Понижение значимости новости"""
    # получаем данные
    callback_data = callback_query.data.split(':')
    reason_to_delete = callback_data[1]
    article_id_to_delete = int(callback_data[2])
    from_user = callback_query.from_user
    chat_id, user_first_name = from_user.id, from_user.first_name

    apd_obj = ArticleProcessAdmin()
    if reason_to_delete == 'cancel':
        await callback_query.message.answer(text='Удаление отменено.')
        user_logger.info('Отмена действия - /delete_article')
    else:
        result = apd_obj.change_score_article_by_id(article_id_to_delete)
        if result:
            await callback_query.message.answer(text='Новость удалена.')
            user_logger.info(
                f'*{chat_id}* {user_first_name} - /delete_article : '
                f'админ понизил значимость новости по причине {reason_to_delete} - id={article_id_to_delete}'
            )
        else:
            await callback_query.message.answer(text='Возникла ошибка, попробуйте в другой раз.')
            user_logger.critical(
                f'*{chat_id}* {user_first_name} - /delete_article : '
                f'не получилось понизить значимость новости с id {article_id_to_delete}'
            )

    # обновляем кнопки на одну не активную
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Команда использована', callback_data='none'))
    await callback_query.message.edit_reply_markup(reply_markup=keyboard.as_markup())


@router.message(Command('dailynews'))
async def dailynews(message: types.Message) -> None:
    user = json.loads(message.from_user.model_dump_json())
    admin_flag = await is_admin_user(user)
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if admin_flag:
        user_df = pd.read_sql_table('whitelist', con=database.engine, columns=['user_id', 'username', 'subscriptions'])
        await subscriptions_newsletter(message.bot, user_df, client_hours=20, commodity_hours=20)
    else:
        user_logger.critical(f'*{chat_id}* {full_name} - {user_msg}. МЕТОД НЕ РАЗРЕШЕН!')


async def delete_newsletter_menu(message: Union[types.CallbackQuery, types.Message]) -> None:
    """Отправляет или изменяет сообщение, формируя там клавиатуру выбора типов сообщений"""
    keyboard = kb_maker.get_message_types_kb()
    msg_text = (
        'Выберите рассылку, сообщения по которой хотите удалить.\n\n'
        'Удалены могут быть лишь те сообщения, с момента отправки которых прошло менее 48 часов.'
    )

    # Проверяем, что за тип апдейта. Если Message - отправляем новое сообщение
    if isinstance(message, types.Message):
        await message.answer(msg_text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)

    # Если CallbackQuery - изменяем это сообщение
    else:
        call = message
        await call.message.edit_text(msg_text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)


@router.message(Command('delete_newsletter_messages'))
async def delete_newsletter_messages(message: types.Message) -> None:
    """
    Формирует меню для выбора типа сообщения, по которому будут удалены все сообщения с этим типом младше 48 часов

    :param message: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    user = json.loads(message.from_user.model_dump_json())
    admin_flag = await is_admin_user(user)
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text

    if admin_flag:
        await delete_newsletter_menu(message)
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
    else:
        await message.answer('У Вас недостаточно прав для использования данной команды.')
        user_logger.warning(f'*{chat_id}* {full_name} - {user_msg} : недостаточно прав для команды')


@router.callback_query(ApproveDeleteMessageByType.filter())
async def approve_delete_messages_by_type(callback_query: types.CallbackQuery, callback_data: ApproveDeleteMessageByType) -> None:
    """
    Формирует сообщение с подтверждением действия по удалению сообщений выбранного типа

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе информацию o message_type_id
    """
    chat_id = callback_query.message.chat.id
    user_msg = BACK_TO_DELETE_NEWSLETTER_MSG_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    msg_type_descr = message_types[callback_data.message_type_id]['description']
    msg_text = (
        f'Вы уверены, что хотите удалить сообщения с типом "<b>{msg_type_descr}</b>", которые были отправлены за последние 48 часов, '
        f'у всех пользователей?'
    )
    keyboard = kb_maker.get_approve_delete_messages_by_type_kb(callback_data.message_type_id)

    await callback_query.message.edit_text(text=msg_text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(DeleteMessageByType.filter())
async def delete_messages_by_type(callback_query: types.CallbackQuery, callback_data: DeleteMessageByType) -> None:
    """
    Удаляет сообщения переданного типа

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param callback_data: Объект, содержащий в себе информацию o message_type_id
    """
    chat_id = callback_query.message.chat.id
    user_msg = BACK_TO_DELETE_NEWSLETTER_MSG_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"

    user_msgs_df = get_messages_by_type(callback_data.message_type_id)
    msg_type_descr = message_types[callback_data.message_type_id]['description']

    for _, row in user_msgs_df.iterrows():
        user_id = row['user_id']
        message_ids = row['message_ids']

        for i in range(0, len(message_ids), TG_DELETE_MESSAGE_IDS_LEN_LIMIT):
            try:
                ids = message_ids[i: i + TG_DELETE_MESSAGE_IDS_LEN_LIMIT]
                await callback_query.bot.delete_messages(
                    user_id, ids, config.DELETE_TG_MESSAGES_TIMEOUT
                )
                delete_messages(user_id, ids)
            except TelegramBadRequest as e:
                info_msg = f'Не удалось удалить сообщения у пользователя {user_id}: %s'
                logger.error(info_msg, e)
        logger.info(f'Удаление сообщений типа {msg_type_descr} у пользователя {user_id} завершено')

    msg_text = (
        f'Готово!\nСообщения с типом "<b>{msg_type_descr}</b>", отправленные менее 48 часов назад, были удалены у всех пользователей'
    )
    keyboard = None

    await callback_query.message.edit_text(text=msg_text, reply_markup=keyboard, parse_mode='HTML', disable_web_page_preview=True)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(BACK_TO_DELETE_NEWSLETTER_MSG_MENU))
async def back_to_delete_newsletter_msg_menu(callback_query: types.CallbackQuery) -> None:
    """
    Фозвращает пользователя в меню (меняет сообщение, с которым связан колбэк)

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    """
    chat_id = callback_query.message.chat.id
    user_msg = BACK_TO_DELETE_NEWSLETTER_MSG_MENU
    from_user = callback_query.from_user
    full_name = f"{from_user.first_name} {from_user.last_name or ''}"
    await delete_newsletter_menu(callback_query)
    user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')

