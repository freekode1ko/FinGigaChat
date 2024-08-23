"""Файл с константами для подписок"""

from keyboards.subscriptions import callbacks as main_callbacks


SUBS_MENU = 'subscriptions_menu'
END_WRITE_SUBS = 'end_write_subs'
SHOW_ALL_SUBS = 'show_all_subs'


MENU_HEADERS = {
    main_callbacks.SubsMenusEnum.my_subscriptions: 'Просмотр подписок\n\n',
    main_callbacks.SubsMenusEnum.change_subscriptions: 'Изменение подписок\n\n',
    main_callbacks.SubsMenusEnum.delete_subscriptions: 'Удаление подписок\n\n',
    main_callbacks.SubsMenusEnum.delete_all_subscriptions: 'Удаление всех подписок\n\n',
}
