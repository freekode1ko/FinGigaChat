from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool


@tool
async def get_news_by_name(name: str, config: RunnableConfig):
    """Возвращает пользователю текст с новостями по компании по заданному названию компании.

    Args:
        name (str): только название компании в именительном падеже.
    return:
        (str): Текст с новостями по компании.
    """
    # TODO: Достать 10 новостей и сформировать суммаризированный текст по этим новостям
    print(f"Вызвана get_news_by_name с параметром {name}")
    msg = f'Новости по: {name}. Суммаризированные новости'
    return msg
