from copy import deepcopy

BOT_FEATURES_DATA = {
    'news': 'Меню новостей, отображение новостей по коммодам, клиентам, общим темам.',

    'analytics_menu': 'Меню аналитики, отображение отчетов с CIB Research.',

    'quotes_menu': 'Меню котировок, отображение различных показателей в виде текста и картинок, немного данных от CIB Research.',

    'clients_menu': 'Меню клиентов, просмотр новостей, отчетов, фин показателей и др. о клиентах.',

    'products_menu': 'Меню продуктов, hot offers, продуктовая полка, господдержка - отчеты.',

    'subscriptions_menu': 'Меню подписок, управление своими подписками (клиенты, отрасли, коммоды, аналитика, тг).',

    'notes': 'Формирование записок.',

    'meeting': 'Формирование напоминания о предстоящей встрече.',

    'knowledgebase': 'Диалог с вопросно-ответной системой.',

    'common': 'Общая базовая функциональность в боте: /start, /help и др.',

    'admin': 'Команды доступные только для админов бота.',


}

USER_FEATURES_DATA = deepcopy(BOT_FEATURES_DATA)
USER_FEATURES_DATA.pop('admin')

USERS_ROLES_DATA = {
    'admin': 'Администратор бота. Доступны все команды, в том числе секретные: по изменению состояния БД или бота.',
    'user': 'Пользователь бота. Доступны все публичные команды и функции.'
}

ROLE_RIGHTS = {
    'admin': BOT_FEATURES_DATA.keys(),
    'user': USER_FEATURES_DATA.keys(),
}

ADMIN_CONTACTS = [
    'oddryabkov@sberbank.ru',
    'mankorolkov@sberbank.ru',
    'nabaturin@sberbank.ru',
    'aserggavrilov@sberbank.ru',
    'TRMagazov@sberbank.ru',
    'aelapikova@sberbank.ru',
]
