from app.model.plan import Plan
from app.ai.llm import LLMProvider
from app.repository.prompt import PromptRepository
from state import StateHolder
from app.services.trace import TraceService

class AgentPlan:
    def __init__(self, llm: LLMProvider, prompt_repository: PromptRepository, trace_service: TraceService):
        self.llm = llm
        self.prompt_repository = prompt_repository
        self.trace_service = trace_service

    def invoke(self, state: StateHolder, trace: TraceService) -> Plan:
        """
        Creates a plan based on the current state.
        Returns a dict with at least a 'tool' key.
        """
        # Implement your planning logic here
        pass