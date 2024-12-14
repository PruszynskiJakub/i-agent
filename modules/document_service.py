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
        """
        Translate a document from source language to target language
        
        Args:
            params: Dictionary containing source_lang and target_lang
            document: Document to translate
            
        Returns:
            Translated document
        """
        source_lang = params.get("source_lang")
        target_lang = params.get("target_lang")
        
        if not source_lang or not target_lang:
            raise ValueError("Both source_lang and target_lang are required")

        # Get translation prompt from Langfuse if available
        prompt_template = None
        if self.langfuse_service:
            try:
                prompt = self.langfuse_service.get_prompt(
                    name="document_translate",
                    prompt_type="chat",
                    fallback=[
                        {"role": "system", "content": "You are a professional translator."},
                        {"role": "user", "content": "Translate the following text from {source_lang} to {target_lang}:\n\n{text}"}
                    ]
                )
                if prompt:
                    prompt_template = prompt.compile(
                        source_lang=source_lang,
                        target_lang=target_lang,
                        text=document["content"]
                    )
            except Exception as e:
                print(f"Failed to get Langfuse prompt: {e}")

        # Use fallback prompt if Langfuse prompt not available
        if not prompt_template:
            prompt_template = [
                {"role": "system", "content": "You are a professional translator."},
                {"role": "user", "content": f"Translate the following text from {source_lang} to {target_lang}:\n\n{document['content']}"}
            ]

        # Get translation from OpenAI
        translated_content = await self.openai_service.completion(prompt_template)
        
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
