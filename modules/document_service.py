from typing import Dict, Any, Optional

from modules.database_service import DatabaseService
from modules.openai_service import OpenAIService
from modules.langfuse_service import LangfuseService
from modules.types import Document


class DocumentService:
    def __init__(self, database_service: DatabaseService, openai_service: OpenAIService, langfuse_service: Optional[LangfuseService] = None):
        self.database_service = database_service
        self.openai_service = openai_service
        self.langfuse_service = langfuse_service

    async def translate(self, params: Dict[str, Any], document: Document) -> Document:
        source_lang = params.get("source_lang")
        target_lang = params.get("target_lang")
        
        if not source_lang or not target_lang:
            raise ValueError("Both source_lang and target_lang are required")

        # Get translation prompt from Langfuse if available
        prompt = self.langfuse_service.get_prompt(
            name="document_translate",
            prompt_type="text",
            label="latest"
        )

        system_prompt = prompt.compile()

        # Get translation from OpenAI
        translated_content = await self.openai_service.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Translate from {source_lang} to {target_lang}: {document["text"]}"}
            ],
            model = prompt.config.get("model", "gpt-4o-mini")
        )
        
        # Create new translated document
        translated_doc = document.copy()
        translated_doc["content"] = translated_content
        translated_doc["metadata"] = {
            **(document.get("metadata", {})),
            "translated_from": source_lang,
            "translated_to": target_lang
        }
        
        # Store translated document
        self.database_service.store_document(translated_doc)
        
        return translated_doc
