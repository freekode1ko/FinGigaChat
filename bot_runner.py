from aiogram import Bot, Dispatcher, executor, types
from config import bot_token

from aiogram.utils.exceptions import MessageIsTooLong
from module.article_process import ArticleProcess

bot = Bot(token=bot_token)
dp = Dispatcher(bot)


@dp.message_handler()
async def giga_ask(message: types.Message):

    reply_msg = ArticleProcess().process_user_alias(message.text)
    if reply_msg:
        try:
            await message.answer(reply_msg, parse_mode='HTML', protect_content=True, disable_web_page_preview=True)
        except MessageIsTooLong:
            articles = reply_msg.split('\n\n')
            for article in articles:
                await message.answer(article, parse_mode='HTML', protect_content=True, disable_web_page_preview=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
