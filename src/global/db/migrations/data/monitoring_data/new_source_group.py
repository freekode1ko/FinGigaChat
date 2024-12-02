rename_parser_source_dict = {
    'Обзорв выплат по': 'Обзор выплат по',
    'Обзор итогов заседания ЦБ': 'Итоги заседания ЦБ',
    'Экономика': 'Экономика РФ',
}

article_source_group = [
    {'name': 'Отраслевые новости (тг)', 'name_latin': 'tg_articles'},
    {'name': 'Новости по сущностям', 'name_latin': 'subject_articles'},
]

research_source_group = [
    {'name': 'Экономика РФ', 'name_latin': 'eco cib'},
    {'name': 'Сырьевые товары', 'name_latin': 'commodities cib'},
    {'name': 'Обзор рынка процентных ставок', 'name_latin': 'interest_rate_review'},
    {'name': 'Валютный рынок и процентные ставки', 'name_latin': 'fx_and_rates'},
    {'name': 'Ежемесячный обзор по мягким валютам', 'name_latin': 'monthly_soft_currency'},
    {'name': 'Ежемесячный обзор по юаню', 'name_latin': 'monthly_yuan_review'},
    {'name': 'Прогноз валютного рынка на', 'name_latin': 'fx_market_forecast'},
    {'name': 'Прогноз итогов заседания ЦБ РФ', 'name_latin': 'cb_meeting_forecast'},
    {'name': 'Итоги заседания ЦБ', 'name_latin': 'cb_meeting_summary'},
    {'name': 'Обзор выплат по', 'name_latin': 'payout_review'},
    {'name': 'Долговые рынки сегодня', 'name_latin': 'debt_markets_today'},
    {'name': 'Итоги аукционов ОФЗ', 'name_latin': 'ofz_auction_summary'},
    {'name': 'Обзор выплат по', 'name_latin': 'payout_overview'},
]

new_source_group = article_source_group + research_source_group

CIB_RESEARCH_SOURCE_GROUP_NAME_LATIN = 'cib_research'
