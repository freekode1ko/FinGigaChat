import keyboards.news.callbacks
from keyboards.subscriptions.news.industry import callbacks
from keyboards.subscriptions.news.news_keyboards import BaseKeyboard


keyboard = BaseKeyboard(callbacks, keyboards.news.callbacks.GetIndustryNews, can_write_subs=False)
