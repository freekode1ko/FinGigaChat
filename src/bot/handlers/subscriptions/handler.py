"""Файл с хендлерами подписок"""
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware


from constants import subscriptions as callback_prefixes
from db.api.telegram_group import telegram_group_db
from db.api.user_client_subscription import user_client_subscription_db
from db.api.user_commodity_subscription import user_commodity_subscription_db
from db.api.user_industry_subscription import user_industry_subscription_db
from db.api.user_research_subscription import user_research_subscription_db
from db.api.user_telegram_subscription import user_telegram_subscription_db
from keyboards.subscriptions import constructors as keyboards
from log.bot_logger import user_logger
from utils.base import is_user_has_access, send_or_edit

router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message use chat action 'typing'


@router.callback_query(F.data.startswith(callback_prefixes.END_WRITE_SUBS))
async def subs_menu_end(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    """
    Завершает работу с меню подписок

    :param callback_query: Объект, содержащий в себе информацию по отправителю, чату и сообщению
    :param state: Состояние FSM
    """
    await state.clear()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.edit_text(text='Формирование подписок завершено')


async def subs_menu(message: types.CallbackQuery | types.Message) -> None:
    """
    Формирует меню подписок

    :param message: types.CallbackQuery | types.Message
    """
    keyboard = keyboards.get_subscriptions_menu_kb()
    msg_text = (
        'Меню управления подписками:\n\n'
        'Выберете раздел подписок, который вы хотели бы изменить.\n\n'
        'Новости из телеграм каналов и доверенных источников\n\n'
        'Аналитика - SberCIB Investment Research\n\n'
    )
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

    if await is_user_has_access(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - {user_msg}')
        await subs_menu(message)
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(F.data.startswith(callback_prefixes.SHOW_ALL_SUBS))
async def show_all_subs(callback_query: types.CallbackQuery) -> None:
    user_id = callback_query.from_user.id

    list_of_subs = [
        ('*Подиски на клиентов:*\n\n', user_client_subscription_db.get_subscription_df(user_id)),
        ('*Подписки на сырьевые товары:*\n\n', user_commodity_subscription_db.get_subscription_df(user_id)),
        ('*Подписки на отрасли:*\n\n', user_industry_subscription_db.get_subscription_df(user_id)),
        ('*Подписки на аналитические отчеты:*\n\n', user_research_subscription_db.get_subscription_df(user_id)),
    ]
    for tg_group in await telegram_group_db.get_all():
        list_of_subs.append((
            f'*{tg_group.name}:*\n\n',
            user_telegram_subscription_db.get_subscription_df_by_group_id(user_id=user_id, group_id=tg_group.id)
        ))

    subs_not_exist = True

    for sub_title, get_sub_func in list_of_subs:
        if sub_names_list := list((await get_sub_func)['name']):
            subs_not_exist = False
            for name in sub_names_list:
                sub_title += f'- {name}\n'
            await callback_query.message.answer(text=sub_title, parse_mode='Markdown')

    if subs_not_exist:
        callback_query.message.answer(text='У вас нет активных подписок')
