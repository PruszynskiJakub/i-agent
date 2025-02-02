from dataclasses import dataclass
from enum import Enum
from typing import TypedDict, List
from uuid import UUID

class DocumentType(Enum):
    """Type of document content"""
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    TEXT = "text"


class DocumentMetadata(TypedDict, total=False):
    """Metadata for a document"""
    type: DocumentType  # Type of document content
    source: str # url or path
    parent_document_uuid: UUID  # UUID of the source document if this is derived from another document
    mime_type: str
    content_type: str # chunk or full
    name: str
    description: str   # A brief description of the document's content
    images: List[str]  # List of image URLs found in the document
    urls: List[str]    # List of URLs found in the document

@dataclass
class Document:
    """A document that can be processed by the agent"""
    uuid: UUID
    conversation_uuid: str
    text: str
    metadata: DocumentMetadata