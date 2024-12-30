from model.action import ActionResult
from repository.prompt import PromptRepository


class YnabService:
    def __init__(self, prompt_repository: PromptRepository):
        self.prompt_repository = prompt_repository

    def add_transactions(self, query: str, trace) -> ActionResult: 
        pass
