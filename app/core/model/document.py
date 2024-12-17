from typing import List, TypedDict
from uuid import UUID


class DocumentMetadata(TypedDict, total=False):
    """Metadata for a document"""
    source: str
    parent_document_uuid: UUID  # UUID of the source document if this is derived from another document
    mime_type: str
    name: str
    description: str   # A brief description of the document's content
    images: List[str]  # List of image URLs found in the document
    urls: List[str]    # List of URLs found in the document

class Document(TypedDict, total=True):
    """A document that can be processed by the agent"""
    uuid: UUID
    conversation_uuid: str
    text: str
    metadata: DocumentMetadata