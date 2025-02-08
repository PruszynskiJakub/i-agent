import asyncio
from typing import Dict, List
from uuid import UUID

from llm.tracing import create_event, create_generation, end_generation
from llm import open_ai
from llm.prompts import get_prompt
from models.document import Document, DocumentType
from utils.document import create_document, restore_placeholders
from db.document import find_document_by_uuid


async def _summarize(params: Dict, span) -> List[Document]:
    """Summarize one or more documents and create a new document from their contents
    
    Args:
        params: Parameters including document UUIDs
        span: Tracing span
        
    Returns:
        Document: The created document
    """
    try:
        # Extract parameters
        document_uuids = params.get("document_uuids", [])
        if not document_uuids:
            create_event(span, "summarize", input=params, output="No document UUIDs provided")
            raise ValueError("document_uuids is required")

        documents = []
        sources = []

        # Fetch and restore documents
        for doc_uuid in document_uuids:
            try:
                uuid = UUID(doc_uuid) if isinstance(doc_uuid, str) else doc_uuid
                document = find_document_by_uuid(uuid)
                if document:
                    restored_doc = restore_placeholders(document)
                    documents.append(restored_doc)
                    sources.append(str(uuid))
                else:
                    raise ValueError(f"Document not found: {doc_uuid}")
            except Exception as e:
                raise

        if not documents:
            raise ValueError("No documents found from provided UUIDs")

        # Merge all document contents
        merged_content = "\n\n---\n\n".join(doc.text for doc in documents)
        source_desc = ", ".join(sources)

        # Get prompt configuration
        prompt = get_prompt(name="tool_document_summarize")
        system_prompt = prompt.compile()
        model = prompt.config.get("model", "gpt-4")

        # Run single summarization on merged content
        generation = create_generation(
            span,
            "summarize_content",
            model,
            merged_content
        )
        
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": merged_content}
            ],
            model=model
        )
        
        end_generation(generation, completion)

        # Create single summary document
        return [create_document(
            text=completion,
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "document_processor",
                "name": "SummarizationResult",
                "description": f"Summary of documents with uuids: {source_desc}",
                "type": DocumentType.DOCUMENT,
                "source_documents": sources
            }
        )]

    except Exception as error:
        create_event(span, "summarize", level="ERROR", input=params, output={"error": str(error)})
        raise
