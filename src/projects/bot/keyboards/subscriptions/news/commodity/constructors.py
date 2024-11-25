"""Клавиатуры по подпискам на новости по сырьевым товарам"""
import keyboards.news.callbacks
from keyboards.subscriptions.news.commodity import callbacks
from keyboards.subscriptions.news.news_keyboards import BaseKeyboard


keyboard = BaseKeyboard(callbacks, keyboards.news.callbacks.GetCommodityNews)
