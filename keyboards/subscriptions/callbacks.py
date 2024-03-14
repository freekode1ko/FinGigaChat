from aiogram.filters.callback_data import CallbackData

from constants.bot.subscriptions import USER_TG_SUBS, TG_CHANNEL_INFO, INDUSTRY_TG_CHANNELS, TG_SUB_ACTION, \
    ADD_ALL_SUBS_BY_DOMAIN


class IndustryTGChannels(CallbackData, prefix=INDUSTRY_TG_CHANNELS):
    industry_id: int = 0
    telegram_id: int = 0
    need_add: bool = False


class UserTGSubs(CallbackData, prefix=USER_TG_SUBS):
    page: int = 0
    delete_tg_sub_id: int = 0


class TGChannelMoreInfo(CallbackData, prefix=TG_CHANNEL_INFO):
    telegram_id: int = 0
    is_subscribed: bool = False
    back: str


class TGSubAction(CallbackData, prefix=TG_SUB_ACTION):
    telegram_id: int
    back: str
    need_add: bool


class AddAllSubsByDomain(CallbackData, prefix=ADD_ALL_SUBS_BY_DOMAIN):
    domain: str




