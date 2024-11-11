data = [
    # QUOTES PARSERS: сбор каждые 15 минут, алерт спустя 1 час после запланированного времени парсинга
    {"name": "Облигации", "period_cron": "0/15 * * * *", "alert_timedelta": 60 * 60},
    {"name": "Экономика", "period_cron": "0/15 * * * *", "alert_timedelta": 60 * 60},
    {"name": "Курсы валют", "period_cron": "0/15 * * * *", "alert_timedelta": 60 * 60},
    {"name": "Металлы", "period_cron": "0/15 * * * *", "alert_timedelta": 60 * 60},

    # GigaParsers PARSERS: мб для котировок веб аппа использовать?  TODO: ???
    {"name": "GigaParsers", "period_cron": "0/15 * * * *", "alert_timedelta": 60*60},

    # RESEARCHES PARSERS:
    # сбор с 8 утра до 20 часов вечера каждый час, алерт спустя 4 часа после запланированного времени парсинга
    {"name": "CIB", "period_cron": "0 8-20 * * *", "alert_timedelta": 4*60*60},
    {"name": "Отчеты CIB Research", "period_cron": "0 8-20 * * *", "alert_timedelta": 4*60*60},
    # сбор каждую пятницу в 18 часов, алерт спустя 1 час
    {"name": "Weekly Pulse", "period_cron": "0 18 * * 5", "alert_timedelta": 60*60},

    # ARTICLE PARSERS: сбор в 3:30 утра каждую ночь, алерт спустя 4 часа
    {"name": "Полианалист", "period_cron": "30 3 * * *", "alert_timedelta": 4*60*60},

    # ARTICLE_ONLINE PARSERS: получение новостей от GigaParsers каждые 20 минут, алерт спустя час
    {"name": "Отраслевые новости (тг)", "period_cron": "*/20 * * * *", "alert_timedelta": 60*60},
    {"name": "Новости по сущностям", "period_cron": "*/20 * * * *", "alert_timedelta": 60*60},
  ]
