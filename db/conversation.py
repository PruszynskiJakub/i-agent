from typing import List
from uuid import UUID

from models.document import Document
from .models import ConversationModel, ConversationDocumentModel, DocumentModel


def create_conversation(uuid: str) -> None:
    """Create a new conversation record"""
    ConversationModel.create(
        uuid=uuid,
        name=f"Conversation {uuid[:8]}"  # Use first 8 chars of UUID as default name
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
            metadata=conv_doc.document.metadata
        )
        documents.append(document)
    
    return documents
