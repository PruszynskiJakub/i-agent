import uuid
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

    async def translate(self, params: Dict[str, Any], document: Document, parent_trace=None) -> Document:
        """
        Translate a document from source language to target language with tracing
        
        Args:
            params: Dictionary containing source_lang and target_lang
            document: Document to translate
            parent_trace: Optional parent trace for logging
            
        Returns:
            Translated document
        """
        source_lang = params.get("source_lang")
        target_lang = params.get("target_lang")
        
        # Create translation span
        translation_span = parent_trace.span(
            name="document_translation",
            input={
                "source_lang": source_lang,
                "target_lang": target_lang,
                "document": document
            }
        ) if parent_trace else None
        
        if not source_lang or not target_lang:
            raise ValueError("Both source_lang and target_lang are required")

        try:
            # Get translation prompt from Langfuse if available
            prompt = self.langfuse_service.get_prompt(
                name="document_translate",
                prompt_type="text",
                label="latest"
            )

            system_prompt = prompt.compile()
            model = prompt.config.get("model", "gpt-4o-mini")

            # Create generation observation if we have a parent trace
            generation = parent_trace.generation(
                name="translation_completion",
                model=model,
                input=system_prompt,
            ) if parent_trace else None

            # Get translation from OpenAI
            translated_content = await self.openai_service.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate from {source_lang} to {target_lang}: {document['text']}"}
                ],
                model=model
            )

            # End generation observation if it exists
            if generation:
                generation.end(
                    output=translated_content
                )
        
            # Create new translated document
            translated_doc = document.copy()
            translated_doc["text"] = translated_content
            translated_doc["metadata"] = {
                **(document.get("metadata", {})),
                "translated_from": source_lang,
                "translated_to": target_lang,
                "uuid": str(uuid.uuid4()),  # Override uuid with a new one
                "source": document['metadata']['uuid'],
                "description": f"Translation of document {document['metadata']['uuid']} from {source_lang} to {target_lang}"
            }
            # Store translated document
            self.database_service.store_document(translated_doc)

            # End translation span if it exists
            if translation_span:
                translation_span.end(
                    output={
                        "result": f"Successfully translated document from {source_lang} to {target_lang}",
                        "documents": [translated_doc]
                    },
                    level="DEFAULT",
                    status_message="Translation successful"
                )
            
            return {
                "result": f"Successfully translated document from {source_lang} to {target_lang}",
                "documents": [translated_doc]
            }

        except Exception as e:
            # End translation span with error if it exists
            if translation_span:
                translation_span.end(
                    output={"error": str(e)},
                    level="ERROR",
                    status_message=f"Translation failed: {str(e)}"
                )
            raise
