from app.core.agent.answer import Answer
from app.core.agent.describe import Describe
from app.core.agent.execute import Execute
from app.core.agent.plan import Plan
from app.core.agent.state import StateHolder


class Agent:
    def __init__(self, state: StateHolder, plan: Plan, describe: Describe, execute: Execute, answer: Answer):
        self.state = state
        self.plan = plan
        self.describe = describe
        self.execute = execute
        self.answer = answer

    async def run(self):
        pass