import keyboards.news.callbacks
from keyboards.subscriptions.news.client import callbacks
from keyboards.subscriptions.news.news_keyboards import BaseKeyboard


keyboard = BaseKeyboard(callbacks, keyboards.news.callbacks.GetClientNews)
