"""Граф исполнения подготовки ко встречи"""

import re

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END

from agent_app import logger
from utils.tool_functions.preparing_meeting.agent import create_agent
from utils.tool_functions.preparing_meeting.planner import create_planner
from utils.tool_functions.preparing_meeting.replanner import create_replanner
from utils.tool_functions.preparing_meeting.utils import PlanExecute

agent_executor = create_agent()
planner = create_planner()
replanner = create_replanner()
memory = MemorySaver()


async def execute_step(state: PlanExecute, config: RunnableConfig):
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    if re.search('(Рекомендация)|(порекомендовать)', task):
        task_formatted = f"""Для следующего плана: {plan_str}\n\n
                         Тебе задано выполнение шага: {1}, {task}. 
                         Информация о проделанных тобой шагах: {state['past_steps']}"""
    else:
        task_formatted = f"""Для следующего плана: {plan_str}\n\n
                             Тебе задано выполнение шага: {1}, {task}. """
    logger.debug(len(task_formatted.split()))
    logger.debug(f"task_formatted: {task_formatted}")
    config['configurable']['task_text'] = task
    config['configurable']['tasks_left'] = len(plan)
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]},
        config=config
    )
    logger.debug(state)
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
        "past_calls": [task],
        "past_step": agent_response["messages"][-1].content[0:100] + '...\n'
    }


async def plan_step(state: PlanExecute, config: RunnableConfig):
    plan = await planner.ainvoke(
        {"messages": [("user", state["input"])]},
        config=config
    )
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute, config: RunnableConfig):
    logger.debug('Зашли в ноду репланера')
    logger.debug(f'state["past_calls"]: {state["past_calls"]}')
    output = await replanner.ainvoke(
        state,
        config
    )
    if len(output.replan) == 1 and output.replan[0] == '__end__':
        logger.debug('Окончание работы графа')
        return {"response": output.replan[0]}
    else:
        logger.debug('Ответ репланера:')
        logger.debug(output.replan)
        return {"plan": output.replan}


def should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        return "agent"


def create_graph_executable():

    workflow = StateGraph(PlanExecute)

    workflow.add_node("planner", plan_step)
    workflow.add_node("agent", execute_step)
    workflow.add_node("replan", replan_step)
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "agent")
    workflow.add_edge("agent", "replan")
    workflow.add_conditional_edges(
        "replan",
        should_end,
        ["agent", END],
    )
    app = workflow.compile(checkpointer=memory)
    logger.info('Инициализирован граф исполнения агента')
    return app
