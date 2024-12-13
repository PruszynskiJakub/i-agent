from typing import List, Dict, Any, Optional
from .database_service import DatabaseService
from .openai_service import OpenAiService

class DocumentService:
    def __init__(self, database_service: DatabaseService, openai_service: OpenAiService):
        self.database_service = database_service
        self.openai_service = openai_service