from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

@tool
async def rag_news(name: str, config: RunnableConfig):
    pass

@tool
async def rag_cib(name: str, config: RunnableConfig):
    pass

@tool
async def rag_web(name: str, config: RunnableConfig):
    pass