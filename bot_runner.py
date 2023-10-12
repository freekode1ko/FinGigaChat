from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
import warnings
import config

API_TOKEN = config.api_token
psql_engine = config.psql_engine

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler()
async def giga_ask(message: types.Message):
    print('{} - {}'.format(message.from_user.full_name, message.text))
    await message.answer('Добрый день! В настоящий момент на '
                         'сервере ведутся технические работы и загружаются обновления. '
                         'Приносим свои извинения за доставленные неудобства! \n\n'
                         'Прямо сейчас мы делаем наш бот лучше!', protect_content=True)

if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    executor.start_polling(dp, skip_updates=True)
