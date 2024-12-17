from app.ai.llm import LLMProvider
from app.repository.prompt import PromptRepository
from app.services.trace import TraceService


class AgentExecute:
    def __init__(self, llm: LLMProvider, prompt_repository: PromptRepository, trace_service: TraceService):
        self.llm = llm
        self.prompt_repository = prompt_repository
        self.trace_service = trace_service  