"""Перепланировщик"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config import API_KEY, BASE_URL, BASE_MODEL
from utils import Act
from prompts import REPLANER_PLOMPT


replanner_prompt = ChatPromptTemplate.from_template(REPLANER_PLOMPT)

replanner = replanner_prompt | ChatOpenAI(model=BASE_MODEL,
                                          api_key=API_KEY, base_url=BASE_URL,
                                          temperature=0).with_structured_output(Act)
