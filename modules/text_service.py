from typing import Dict, Any, List, Tuple
import re
from uuid import UUID
from modules.types import Document, DocumentMetadata

class TextService:
    """Service for processing and managing text documents"""
    
    def document(self, content: str, metadata: Dict[str, Any] = None) -> Document:
        """
        Creates a Document object from content and metadata
        
        Args:
            content: The text content to process
            metadata: Optional dictionary of metadata about the document
            
        Returns:
            Document object containing the content and metadata
        """
        if metadata is None:
            metadata = {}
            
        # Ensure metadata matches DocumentMetadata type
        document_metadata: DocumentMetadata = {
            "uuid": metadata.get("uuid", UUID(int=0)),
            "conversation_uuid": metadata.get("conversation_uuid", ""),
            "source": metadata.get("source", ""),
            "mime_type": metadata.get("mime_type", ""),
            "name": metadata.get("name", "")
        }
            
        return Document(
            text=content,
            metadata=document_metadata
        )
