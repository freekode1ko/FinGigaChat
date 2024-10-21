"""Файл с командами для бота"""

PUBLIC_COMMANDS: list[dict] = [
    {
        'command': 'news',
        'description': 'Новости',
    },
    {
        'command': 'analytics_menu',
        'description': 'Аналитика',
    },
    {
        'command': 'quotes_menu',
        'description': 'Котировки',
    },
    {
        'command': 'company_menu',
        'description': 'Компании',
    },
    {
        'command': 'products_menu',
        'description': 'Продукты (Beta)',
    },
    {
        'command': 'subscriptions_menu',
        'description': 'Меню подписок',
    },
    {
        'command': 'notes',
        'description': 'Заметки',
    },
    {
        'command': 'meeting',
        'description': 'Встречи (Beta)',
    },
    {
        'command': 'knowledgebase',
        'description': 'Спросить у Базы Знаний',
    },
    # {
    #     'command': 'get_tg_news',
    #     'description': 'Сводка новостей из telegram каналов по отраслям',
    # },
    {
        'command': 'help',
        'description': 'Информация о боте',
    },
    # {
    #     'command': 'gigachat',
    #     'description': 'Переход в режим общения с GigaChat',
    # },
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
    # {
    #     'command': 'delete_article',
    #     'description': 'Удалить новость',
    # },

]

SECRET_COMMANDS: list[dict] = [
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
    {
        'command': 'web_app',
        'description': 'Отправить кнопку с веб апом',
    },
]
