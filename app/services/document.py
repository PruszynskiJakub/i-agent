from app.model.document import Document
from app.repository.prompt import PromptRepository


class DocumentService:
    def __init__(self, prompt_repository: PromptRepository):
        self.prompt_repository = prompt_repository

    def translate(self, document: Document) -> Document:
        pass

    def summarize(self, document: Document) -> Document:
        pass

    def synthesize(self, document: Document) -> Document:
        pass
