import pandas as pd
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot_logger import logger, user_logger
from constants.bot.constants import handbook_format
from utils.bot.base import show_ref_book_by_request, user_in_whitelist

# logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(ChatActionMiddleware())  # on every message for admin commands use chat action 'typing'


class RefBookStates(StatesGroup):
    please_add_this = State()


@router.message(Command('referencebook'))
async def reference_book(message: types.Message) -> None:
    chat_id, full_name, user_msg = message.chat.id, message.from_user.full_name, message.text
    if await user_in_whitelist(message.from_user.model_dump_json()):
        user_logger.info(f'*{chat_id}* {full_name} - Запросил справочник')

        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(text='Клиенты', callback_data='ref_books:client'))
        keyboard.row(types.InlineKeyboardButton(text='Бенефициары и ЛПР', callback_data='ref_books:beneficiaries'))
        keyboard.row(types.InlineKeyboardButton(text='Commodities', callback_data='ref_books:commodity'))

        await message.answer('Выберите какой справочник вам интересен:', reply_markup=keyboard.as_markup())
    else:
        user_logger.info(f'*{chat_id}* Неавторизованный пользователь {full_name} - {user_msg}')


@router.callback_query(F.data.startswith('ref_books'))
async def ref_books(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    await state.set_state(RefBookStates.please_add_this)
    from_user = callback_query.from_user
    chat_id, user_first_name = from_user.id, from_user.first_name
    callback_data = callback_query.data.split(':')
    book = callback_data[1]
    user_logger.info(f'*{chat_id}* {user_first_name} - Запросил справочник по {book}')
    handbooks = [pd.DataFrame(columns=['industry_name', 'object'])]
    what_is_this = ''
    if book == 'client':
        await callback_query.message.answer(text='Справочник по клиентам:')
        handbooks = await show_ref_book_by_request(chat_id, book, logger)
        what_is_this = 'клиенты (холдинги)'
    elif book == 'beneficiaries':
        what_is_this = 'бенефициары и ЛПР'
        pass
        # await bot.send_message(chat_id, text='Справочник по бенефициарам и ЛПР:')
        # handbooks = await show_ref_book_by_request(chat_id, '')
    elif book == 'commodity':
        what_is_this = 'commodities'
        await callback_query.message.answer(text='Справочник по commodities:')
        handbooks = await show_ref_book_by_request(chat_id, book, logger)

    for handbook in handbooks:
        head = handbook['industry_name'].tolist()
        if len(head) > 0:
            block_head = head[0].upper()
            block_body = '\n'.join([news_object.title() for news_object in handbook['object'].tolist()])
        else:
            block_head = ''
            block_body = (
                'Справочник по бенефициарам и ЛПР находится в процессе обновления, '
                'приносим извинения за неудобства. Функционал активной и пассивной '
                'рассылки по бенефициарам остается активным, для этого сформируйте '
                'новый список рассылки, вставив фамилии интересующих лиц и клиентов '
                'или просто введите их диалоговую строку, чтобы получить текущие новости.'
            )

        await callback_query.message.answer(handbook_format.format(block_head, block_body), parse_mode='HTML')
    keyboard = InlineKeyboardBuilder()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='isthisall:yes'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='isthisall:no'))
    await callback_query.message.answer(
        text=f'Все ли Ваши {what_is_this} содержатся в справочнике?\n', reply_markup=keyboard.as_markup()
    )


@router.callback_query(RefBookStates.please_add_this, F.data.startswith('isthisall'))
async def isthisall(callback_query: types.CallbackQuery, state: FSMContext) -> None:
    from_user = callback_query.from_user
    chat_id, user_first_name = from_user.id, from_user.first_name
    callback_data = callback_query.data.split(':')
    need_new = callback_data[1]
    user_logger.info(f'*{chat_id}* {user_first_name} - Пользователь удовлетворен наполнением справочника?  {need_new}')
    if need_new == 'no':
        await callback_query.message.answer(
            text='Если вы не нашли интересующего вас клиента (холдинг), '
            'бенефициара, ЛПР или commodity в списке, напишите его наименование в чат.'
            '\nВы также можете написать его альтернативные названия и синонимы. '
            'Мы добавим их в справочник в ближайшее время.\n'
            'При возникновении дополнительных вопросов можно '
            'обращаться к Максиму Королькову',
        )
        await continue_isthisall(state=state)
    else:
        await callback_query.message.answer(text='Спасибо за обратную связь!')
        await state.clear()


@router.message(RefBookStates.please_add_this)
async def continue_isthisall(message: types.Message, state: FSMContext) -> None:
    await state.update_data(please_add_this=message.text)  # FIXME зачем оно такое?
    data = await state.get_data()
    user_logger.info(f"Пользовать {message.from_user.full_name} просит добавить в справочник: {data.get('please_add_this')}")
    await state.clear()
    await message.answer('Спасибо за обратную связь, мы добавим их как можно скорее')
