from typing import Dict, List
from uuid import UUID

from llm.tracing import create_event
from models.document import Document, DocumentType
from utils.document import create_document
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

        contents = []
        sources = []

        # Process documents
        for doc_uuid in document_uuids:
            try:
                uuid = UUID(doc_uuid) if isinstance(doc_uuid, str) else doc_uuid
                document = find_document_by_uuid(uuid)
                if document:
                    contents.append(document.text)
                    sources.append(str(uuid))
                    create_event(span, "summarize_document", input=doc_uuid, output="Document processed")
                else:
                    create_event(span, "summarize_document", level="ERROR", input=doc_uuid, output="Document not found")
                    raise ValueError(f"Document not found: {doc_uuid}")
            except Exception as e:
                create_event(span, "summarize_document", level="ERROR", input=doc_uuid, output=str(e))
                raise

        if not contents:
            raise ValueError("No content found from provided documents")

        # Combine all content
        combined_content = "\n\n".join(contents)
        source_desc = ", ".join(sources)

        # Create document
        return [create_document(
            text=combined_content,
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "summarize",
                "name": "combined_documents",
                "description": f"Summarized documents: {source_desc}",
                "type": DocumentType.FILE,
                "source_documents": document_uuids
            }
        )]

    except Exception as error:
        create_event(span, "summarize", level="ERROR", input=params, output={"error": str(error)})
        raise
