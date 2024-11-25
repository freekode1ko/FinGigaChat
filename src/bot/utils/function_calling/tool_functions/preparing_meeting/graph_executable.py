"""Граф исполнения подготовки ко встречи"""

from langgraph.graph import StateGraph, START, END

from utils.function_calling.tool_functions.preparing_meeting.utils import PlanExecute, Response
from utils.function_calling.tool_functions.preparing_meeting.planner import create_planner
from utils.function_calling.tool_functions.preparing_meeting.replanner import create_replanner
from utils.function_calling.tool_functions.preparing_meeting.agent import create_agent

agent_executor = create_agent()
planner = create_planner()
replanner = create_replanner()

# TODO: глянуть на адекватность
# TODO: переписать на русский, что не на русском
# TODO: добавить в какую-нибудь документацию наглядный вид графа


async def execute_step(state: PlanExecute):
    plan = state["plan"]
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    task = plan[0]
    task_formatted = f"""For the following plan:
{plan_str}\n\nYou are tasked with executing step {1}, {task}. Information obtained in the previous steps {state['past_steps']}"""
    agent_response = await agent_executor.ainvoke(
        {"messages": [("user", task_formatted)]}
    )
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }


async def plan_step(state: PlanExecute):
    plan = await planner.ainvoke({"messages": [("user", state["input"])]})
    return {"plan": plan.steps}


async def replan_step(state: PlanExecute):
    output = await replanner.ainvoke(state)
    if isinstance(output.action, Response):
        return {"response": output.action.response}
    else:
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
