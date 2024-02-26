from typing import List

PUBLIC_COMMANDS: List[dict] = [
    {
        'command': 'help',
        'description': 'Информация о боте',
    },
    {
        'command': 'gigachat',
        'description': 'Переход в режим общения с GigaChat',
    },
    {
        'command': 'eco',
        'description': 'Экономика',
    },
    {
        'command': 'bonds',
        'description': 'Облигации',
    },
    {
        'command': 'fx',
        'description': 'Курсы валют',
    },
    {
        'command': 'commodities',
        'description': 'Сырьевые товары',
    },
    {
        'command': 'view',
        'description': 'Витрина данных',
    },
    {
        'command': 'newsletter',
        'description': 'Weekly pulse',
    },
    {
        'command': 'referencebook',
        'description': 'Справочник',
    },
    {
        'command': 'subscriptions_menu',
        'description': 'Меню подписок',
    },
    {
        'command': 'industry_tgnews',
        'description': 'Сводка новостей из telegram каналов по отраслям',
    },
    {
        'command': 'tg_subscriptions_menu',
        'description': 'Подписки на telegram каналы',
    },
    {
        'command': 'delete_article',
        'description': 'Удалить новость',
    },
]

SECRET_COMMANDS: List[dict] = [
    {
        'command': 'admin_help',
        'description': 'Подсказка для админа',
    },
    {
        'command': 'sendtoall',
        'description': 'Отправить сообщение всем пользователем от имени бота',
    },
    {
        'command': 'addmetowhitelist',
        'description': 'Добавить в список пользователей',
    },
    {
        'command': 'show_article',
        'description': 'Показать новость',
    },
    {
        'command': 'change_summary',
        'description': 'Изменить краткое содержание',
    },
    {
        'command': 'daylynews',
        'description': 'Краткая сводка новостей',
    },
    {
        'command': 'start',
        'description': 'Начать работу с ботом',
    },
]
