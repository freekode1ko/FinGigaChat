from aiogram.filters.callback_data import CallbackData

from constants import subscriptions as callback_prefixes


class AddAllSubsByDomain(CallbackData, prefix=callback_prefixes.ADD_ALL_SUBS_BY_DOMAIN):
    domain: str
