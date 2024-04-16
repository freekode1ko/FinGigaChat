from aiogram.filters.callback_data import CallbackData

from constants import subscriptions as callback_prefixes


class IndustryTGChannels(CallbackData, prefix=callback_prefixes.INDUSTRY_TG_CHANNELS):
    industry_id: int = 0
    telegram_id: int = 0
    need_add: bool = False


class UserTGSubs(CallbackData, prefix=callback_prefixes.USER_TG_SUBS):
    page: int = 0
    delete_tg_sub_id: int = 0


class TGChannelMoreInfo(CallbackData, prefix=callback_prefixes.TG_CHANNEL_INFO):
    telegram_id: int = 0
    is_subscribed: bool = False
    back: str


class TGSubAction(CallbackData, prefix=callback_prefixes.TG_SUB_ACTION):
    telegram_id: int
    back: str
    need_add: bool
