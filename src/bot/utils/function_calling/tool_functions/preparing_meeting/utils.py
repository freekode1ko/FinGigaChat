"""Вспомогательные абстракции ленгчейна"""

import operator
from typing import Annotated, List, Tuple

from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    past_calls: Annotated[List[Tuple], operator.add]
    past_step: str
    response: str


class Plan(BaseModel):
    """План для выполнения в будущем"""

    steps: List[str] = Field(
        description="различные действия для выполнения, должны быть в отсортированном порядке"
    )


class Replan(BaseModel):
    """Обновленный план"""

    replan: List[str] = Field(
        description="Действие для выполнения. Если ты хочешь закончить и ответить пользователю, replan должен содержать одно задание '__end__'. "
    )
