from typing import List

PUBLIC_COMMANDS: List[dict] = [
    {
        'command': 'help',
        'description': 'Информация о боте',
    },
    {
        'command': 'analytics_menu',
        'description': 'Аналитика',
    },
    {
        'command': 'clients_menu',
        'description': 'Клиенты',
    },
    {
        'command': 'products_menu',
        'description': 'Продукты',
    },
    {
        'command': 'quotes_menu',
        'description': 'Котировки',
    },
    {
        'command': 'subscriptions_menu',
        'description': 'Меню подписок',
    },
    # {
    #     'command': 'gigachat',
    #     'description': 'Переход в режим общения с GigaChat',
    # },
    {
        'command': 'knowledgebase',
        'description': 'Спросить у Базы Знаний',
    },
    {
        'command': 'meeting',
        'description': 'Мои встречи',
    },
    # {
    #     'command': 'referencebook',
    #     'description': 'Справочник',
    # },
    # {
    #     'command': 'newsletter',
    #     'description': 'События недели',
    # },
    # {
    #     'command': 'eco',
    #     'description': 'Экономика',
    # },
    {
        'command': 'industry_tgnews',
        'description': 'Сводка новостей из telegram каналов по отраслям',
    },
    # {
    #     'command': 'delete_article',
    #     'description': 'Удалить новость',
    # },
    {
        'command': 'call_reports',
        'description': 'Call reports',
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
        'command': 'addme',
        'description': 'Зарегистрироваться',
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
        'command': 'dailynews',
        'description': 'Рассылка краткой сводки новостей всем пользователям',
    },
    {
        'command': 'start',
        'description': 'Начать работу с ботом',
    },
    {
        'command': 'delete_newsletter_messages',
        'description': 'Удаление сообщений, отправленных с помощью пассивной рассылки',
    },
]
