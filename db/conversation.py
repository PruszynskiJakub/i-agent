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
    """Load all documents associated with a conversation"""
    query = (DocumentModel
             .select()
             .join(ConversationDocumentModel)
             .where(ConversationDocumentModel.conversation_uuid == uuid))
    
    documents = []
    for doc_model in query:
        document = Document(
            uuid=UUID(doc_model.uuid),
            text=doc_model.text,
            metadata=doc_model.metadata
        )
        documents.append(document)
    
    return documents
