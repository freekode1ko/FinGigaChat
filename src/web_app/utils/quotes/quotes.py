from utils.quotes.loader import load_cbr_quotes, load_moex_quotes
from utils.quotes.updater import update_all_cbr, update_all_moex


async def get_quotes_data():
    """Обновляет данные о котировказ из конфига, перед запуском приложения"""

    await load_cbr_quotes()

    await update_all_cbr()

    await load_moex_quotes()

    await update_all_moex()
