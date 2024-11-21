"""Промпты"""

# TODO: переписать на русский

BASE_PROMPT = 'Ты ассистент менеджера по работе с ключевыми клиентами в крупном банке. ' \
              'Менеджер задает тебе какой-то вопрос или просит что-то сделать. ' \
              'Тебе даны инструменты, чтобы ты мог это выполнить. ' \
              'Ни в коем случае не используй более одного вызова инструмента в своей работе.'

PLANER_PROMPT = """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps."""

REPLANER_PLOMPT = """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Your objective was this:
{input}

Your original plan was this:
{plan}

You have currently done the follow steps:
{past_steps}

Update your plan accordingly.  If no more steps are needed and you can return to the user, then respond with that. Otherwise, fill out the plan. Only add steps to the plan that still NEED to be done. Do not return previously done steps as part of the plan."""
