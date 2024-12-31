import os

from agent.answer import agent_answer
from agent.execute import agent_execute
from agent.plan import agent_plan
from agent.state import AgentState, should_continue
from llm.tracing import create_trace, end_trace


async def agent_run(state: AgentState) -> str:
    trace = create_trace(
        name=state.messages[-1].content[:45],  # First 45 chars of user input as trace name
        user_id=os.getenv("USER", "default_user"),
        metadata={
            'medium': 'slack'
        },
        session_id=state.conversation_uuid,
        input=state.messages[-1].content,
    )

    while should_continue(state):
        plan = await agent_plan(state, trace)

        if plan.tool == 'final_answer':
            break

        await agent_execute(state, plan, trace)

    new_state = await agent_answer(state, trace)
    final_answer = new_state.messages[-1].content

    end_trace(trace, output=final_answer)
    return final_answer
