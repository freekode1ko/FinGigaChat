"""Конфигурации рассылок

Модуль с конфигурацией рассылок новостей по:
- подпискам на клиентов, сырьевые товары, отрасли
- подпискам на телеграм каналы
- викли пульс
- подпискам на отчеты cib research
"""
import calendar
import datetime

from utils import newsletter

NEWSLETTER_CONFIG = [
    # send daily news
    {
        'executor': newsletter.subscriptions_newsletter,
        'newsletter_info': 'подпискам',
        'params': [
            {
                'weekday': -1,
                'send_time': '17:00',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=6, minutes=30)},
            }
        ],
    },
    {
        'executor': newsletter.subscriptions_newsletter,
        'newsletter_info': 'подпискам',
        'params': [
            {
                'weekday': -1,
                'send_time': '10:30',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=17, minutes=30)},
            }
        ],
    },

    # пассивная рассылка новостей по подпискам на тг каналы
    # пн - 09:00 (за период с 16:00 прошлой пятницы дня до 09:00), 17:30 (за период с 09:00 этого дня до 17:30)
    # вт, ср, чт - 09:00 (за период с 17:30 предыдущего дня до 09:00), 17:30 (за период с 09:00 этого дня до 17:30)
    # пт - 09:00 (за период с 17:30 предыдущего дня до 09:00), 16:00 (за период с 16:00 предыдущей пятницы до 16:00)
    {
        'executor': newsletter.tg_newsletter,
        'newsletter_info': 'подпискам на telegram каналы',
        'params': [
            {
                'weekday': calendar.MONDAY,
                'send_time': '09:00',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=65)},
            },
            {
                'weekday': calendar.MONDAY,
                'send_time': '17:30',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=8, minutes=30)},
            },
            {
                'weekday': calendar.TUESDAY,
                'send_time': '09:00',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=15, minutes=30)},
            },
            {
                'weekday': calendar.TUESDAY,
                'send_time': '17:30',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=8, minutes=30)},
            },
            {
                'weekday': calendar.WEDNESDAY,
                'send_time': '09:00',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=15, minutes=30)},
            },
            {
                'weekday': calendar.WEDNESDAY,
                'send_time': '17:30',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=8, minutes=30)},
            },
            {
                'weekday': calendar.THURSDAY,
                'send_time': '09:00',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=15, minutes=30)},
            },
            {
                'weekday': calendar.THURSDAY,
                'send_time': '17:30',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=8, minutes=30)},
            },
            {
                'weekday': calendar.FRIDAY,
                'send_time': '09:00',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(hours=15, minutes=30)},
            },
            {
                'weekday': calendar.FRIDAY,
                'send_time': '16:00',
                'kwargs': {'newsletter_timedelta': datetime.timedelta(days=7)},
            },
        ],
    },

    # Рассылка слайдов из нового обзора weekly pulse
    {
        'executor': newsletter.weekly_pulse_newsletter,
        'newsletter_info': 'weekly_event',
        'params': [
            {
                'weekday': calendar.MONDAY,
                'send_time': '11:00',
                'kwargs': dict(newsletter_type='weekly_event'),
            }
        ],
    },
    {
        'executor': newsletter.weekly_pulse_newsletter,
        'newsletter_info': 'weekly_result',
        'params': [
            {
                'weekday': calendar.FRIDAY,
                'send_time': '18:00',
                'kwargs': dict(newsletter_type='weekly_result'),
            }
        ],
    },
]

CIB_RESEARCH_NEWSLETTER_PARAMS = {
    'trigger': 'interval',
    'minutes': 10,
    'max_instances': 1,
}
