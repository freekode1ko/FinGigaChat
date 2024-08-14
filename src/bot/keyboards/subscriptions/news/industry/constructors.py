"""Клавиатуры по подпискам на новости по отраслям"""
import keyboards.news.callbacks
from keyboards.subscriptions.news.industry import callbacks
from keyboards.subscriptions.news.news_keyboards import IndustryKeyboards

keyboard = IndustryKeyboards(callbacks, keyboards.news.callbacks.GetIndustryNews, can_write_subs=False)
