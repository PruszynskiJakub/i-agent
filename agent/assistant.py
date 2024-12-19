import os

from agent.answer import AgentAnswer
from agent.execute import AgentExecute
from agent.plan import AgentPlan
from agent.state import StateHolder
from services.trace import TraceService


class Assistant:
    def __init__(self, state: StateHolder, trace_service: TraceService, plan: AgentPlan, execute: AgentExecute,
                 answer: AgentAnswer):
        self.state = state
        self.trace_service = trace_service
        self.plan = plan
        self.execute = execute
        self.answer = answer

    async def run(self):

        trace = self.trace_service.create_trace(
            name = self.state.messages[-1].content[:45],  # First 45 chars of user input as trace name
            user_id= os.getenv("USER", "default_user"),
            session_id= self.state.conversation_uuid,
            input= self.state.messages[-1].content,
        )

        while self.state.should_continue():
            plan = await self.plan.invoke(self.state, trace)

            if plan.tool == 'final_answer':
                break

            await self.execute.invoke(self.state, plan, trace)

        final_answer = await self.answer.invoke(self.state, trace)

        self.trace_service.end_trace(trace, output=final_answer)
        return final_answer
