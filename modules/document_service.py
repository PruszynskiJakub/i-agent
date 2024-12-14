from typing import Dict, Any

from database_service import DatabaseService
from openai_service import OpenAIService
from types import Document


class DocumentService:
    def __init__(self, database_service: DatabaseService, openai_service: OpenAIService):
        self.database_service = database_service
        self.openai_service = openai_service

    def translate(self, params: Dict[str, Any], document: Document) -> Document:

        return document
