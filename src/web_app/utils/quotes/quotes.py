from utils.quotes.loader import load_cbr_quotes, load_MOEX_quotes
from utils.quotes.updater import update_all_cbr


async def get_quotes_data():
    """Обновляет данные о котировказ из конфига, перед запуском приложения"""

    await load_cbr_quotes()

    await update_all_cbr()

    await load_MOEX_quotes()

    # existing_quotes = []
    # not_existing_quotes = []

    # Проверка, что уже есть в базе

    # quotes = await session.execute(sa.select(models.Quotes))
    # for i in session.scalars(quotes):
    #     if i in quotes_data:  # FIXME изменить in проверку
    #         existing_quotes.append(i)
    #     not_existing_quotes.append(i)

    # await update_quotes_params(existing_quotes)  # Обновить данные, если изменились
    # await add_new_quotes(not_existing_quotes)  # Добавить новые
