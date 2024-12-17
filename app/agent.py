from app.agent.answer import Answer
from app.agent.execute import Execute
from app.agent.plan import Plan
from app.agent.state import StateHolder
from app.services.trace import TraceService


class Agent:
    def __init__(self, state: StateHolder, trace_service: TraceService, plan: Plan, execute: Execute, answer: Answer):
        self.state = state
        self.trace_service = trace_service
        self.plan = plan
        self.execute = execute
        self.answer = answer

    async def run(self):

        trace = self.trace_service.create_trace()

        while self.state.should_continue(): 
            plan = self.plan.invoke(self.state, trace)

            if plan['tool'] == 'final_answer':
                break

            self.execute.invoke(self.state, plan, trace)

        final_answer = self.answer.invoke(self.state, trace)

        self.trace_service.end_trace(trace, output=final_answer)
        return final_answer
