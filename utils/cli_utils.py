from typing import Tuple


def get_period(period: str) -> Tuple[int, int, str]:
    if not isinstance(period, str):
        raise TypeError('Неверный тип параметра period.')
    period_scales = {
        's': 1,
        'm': 60,
        'h': 60 * 60,
        'd': 24 * 60 * 60,
    }
    period_scales_txt = {
        1: 'секунд',
        60: 'минут',
        60 * 60: 'часов',
        24 * 60 * 60: 'дней',
    }
    scale = period_scales.get(period[-1:], period_scales['m'])
    scale_txt = period_scales_txt[scale]
    if period.isdigit():
        period = int(period)
    elif period[:-1].isdigit():
        period = int(period[:-1])
    else:
        raise ValueError('Неверное значение параметра period.')
    return period, scale, scale_txt
