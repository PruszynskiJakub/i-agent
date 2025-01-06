import os

from agent.answer import agent_answer
from agent.define import agent_define
from agent.execute import agent_execute
from agent.plan import agent_plan
from agent.state import AgentState, should_continue, increment_current_step
from llm.tracing import create_trace, end_trace


async def agent_run(in_state: AgentState) -> str:
    state = in_state

    trace = create_trace(
        name=in_state.messages[-1].content[:45],  # First 45 chars of user input as trace name
        user_id=os.getenv("USER", "default_user"),
        metadata={
            'medium': 'slack'
        },
        session_id=state.conversation_uuid,
        input=state.messages[-1].content,
    )

    while should_continue(state):
        state = await agent_plan(state, trace)

        if state.step_info.tool == 'final_answer':
            break

        state = await agent_define(state, trace)
        state = await agent_execute(state, trace)
        state = increment_current_step(state)

    state = await agent_answer(state, trace)
    final_answer = state.messages[-1].content

    end_trace(trace, output=final_answer)
    return final_answer
