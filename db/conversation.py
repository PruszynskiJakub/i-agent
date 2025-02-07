from typing import List
from uuid import UUID

from models.document import Document
from .models import ConversationModel, ConversationDocumentModel, DocumentModel


def create_conversation_if_not_exists(uuid: str) -> None:
    """Create a new conversation record if it doesn't already exist"""
    conversation, created = ConversationModel.get_or_create(
        uuid=uuid,
        defaults={'name': f"Conversation {uuid[:8]}"}  # Use first 8 chars of UUID as default name
    )


def load_conversation_documents(uuid: str) -> List[Document]:
    """Load all documents associated with a conversation through conversation_documents table"""
    query = (ConversationDocumentModel
             .select(DocumentModel)
             .join(DocumentModel)
             .where(ConversationDocumentModel.conversation_uuid == uuid))
    
    documents = []
    for conv_doc in query:
        document = Document(
            uuid=UUID(conv_doc.document.uuid),
            text=conv_doc.document.text,
            conversation_uuid=uuid,
            metadata=conv_doc.document.metadata
        )
        documents.append(document)
    
    return documents
