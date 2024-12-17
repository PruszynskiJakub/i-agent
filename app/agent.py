from app.core.agent.state import StateHolder


class Agent:
    def __init__(self, state: StateHolder, plan:):
        self.state = state
