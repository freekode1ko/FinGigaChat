"""Граф исполнения подготовки ко встречи"""

import re

from langgraph.graph import StateGraph, START, END

from utils.function_calling.tool_functions.preparing_meeting.utils import PlanExecute, Response
from utils.function_calling.tool_functions.preparing_meeting.planner import create_planner
from utils.function_calling.tool_functions.preparing_meeting.replanner import create_replanner
from utils.function_calling.tool_functions.preparing_meeting.agent import create_agent
from utils.function_calling.tool_functions.preparing_meeting.prompts import REPLANER_PROMPT
from langchain_core.runnables import RunnableConfig

agent_executor = create_agent()
planner = create_planner()
replanner = create_replanner()

# TODO: глянуть на адекватность
# TODO: добавить в какую-нибудь документацию наглядный вид графа


async def execute_step(state: PlanExecute, config: RunnableConfig):
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    if re.search('(Рекомендация)|(порекомендовать)', task):
        print('Этап с рекомендацией, добавляем в промпт всю предыдущую информацию')
        task_formatted = f"""Для следующего плана: {plan_str}\n\n
                         Тебе задано выполнение шага: {1}, {task}. 
                         Информация о проделанных тобой шагах: {state['past_steps']}"""
    else:
        task_formatted = f"""Для следующего плана: {plan_str}\n\n
                             Тебе задано выполнение шага: {1}, {task}. """
    print()
    print(len(task_formatted.split()))
    print(f"task_formatted: {task_formatted}")
    print()
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]},
        config={
            'configurable': {
                "message": config['configurable']['message'],
                'buttons': config['configurable']['buttons'],
                'message_text': config['configurable']['message_text'],
                'final_message': config['configurable']['final_message'],
                'task_text': task,
                'tasks_left': len(plan)
            }
        }
    )
    print()
    print(state)
    print()
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
        "past_calls": [task],
        "past_step": agent_response["messages"][-1].content[0:100] + '...\n'
    }


async def plan_step(state: PlanExecute, config: RunnableConfig):
    plan = await planner.ainvoke(
        {"messages": [("user", state["input"])]},
        config={
            'configurable': {
                "message": config['configurable']['message'],
                'buttons': config['configurable']['buttons'],
                'message_text': config['configurable']['message_text'],
                'final_message': config['configurable']['final_message']
            }
        }
    )
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute, config: RunnableConfig):
    print()
    print('Зашли в ноду репланера')
    print(f'state["past_calls"]: {state["past_calls"]}')
    print('Промпт репланера:')
    print(REPLANER_PROMPT.format(input=state['input'],
                                 plan=state['plan'],
                                 past_calls=state['past_calls'],
                                 past_step=state['past_step']))
    output = await replanner.ainvoke(
        state,
        config={
            'configurable': {
                "message": config['configurable']['message'],
                'buttons': config['configurable']['buttons'],
                'message_text': config['configurable']['message_text'],
                'final_message': config['configurable']['final_message']
            }
        }
    )
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
        print()
        print('Ответ репланера:')
        print(output.action.steps)
        print()
        return {"plan": output.action.steps}


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

    app = workflow.compile()

    return app
