import os

from agent.execute import agent_execute
from agent.plan import agent_plan
from agent.answer import agent_answer
from llm_utils.tracing import create_trace, end_trace


async def agent_run(self):
    trace = create_trace(
        name=self.state.messages[-1].content[:45],  # First 45 chars of user input as trace name
        user_id=os.getenv("USER", "default_user"),
        metadata={
            'medium': 'slack'
        },
        session_id=self.state.conversation_uuid,
        input=self.state.messages[-1].content,
    )

    while self.state.should_continue():
        plan = await agent_plan(self.state, trace)

        if plan.tool == 'final_answer':
            break

        await agent_execute(self.state, plan, trace)

    final_answer = await agent_answer(self.state, trace)

    end_trace(trace, output=final_answer)
    return final_answer
