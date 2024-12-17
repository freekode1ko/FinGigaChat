"""Вспомогательные абстракции ленгчейна"""

import operator
from typing import Annotated, List, Tuple, Union

from langgraph.graph.message import AnyMessage, add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# TODO: переписать на русский все


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
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


class Response(BaseModel):
    """Response to user."""

    response: str


class Act(BaseModel):
    """Action to perform."""

    action: Union[Response, Plan] = Field(
        description="Action to perform. If you want to respond to user, use Response. "
        "If you need to further use tools to get the answer, use Plan."
    )
