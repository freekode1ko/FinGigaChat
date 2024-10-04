"""Обновление и загрузка котировок"""
from utils.quotes.loader import load_cbr_metals, load_cbr_quotes, load_moex_quotes, load_yahoo_quotes
from utils.quotes.updater import update_all_cbr, update_all_moex, update_cbr_metals


async def load_quotes():
    """Первичная загрузка данные о котировках в бд"""
    await load_cbr_quotes()
    await load_moex_quotes()
    await load_yahoo_quotes()
    await load_cbr_metals()


async def update_quote_data():
    """Обновляет данные о котировках из конфига, перед запуском приложения"""
    for func in (update_all_cbr, update_all_moex, load_yahoo_quotes, update_cbr_metals):
        for _ in range(5):
            try:
                await func()
            except Exception as e:
                continue
            else:
                break
