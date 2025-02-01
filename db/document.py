from typing import List, Optional, Dict, Any
from uuid import UUID
from db.models import DocumentModel
from models.document import Document


def save_document(document: Document | Dict[str, Any]) -> None:
    """
    Save a document to the database
    
    Args:
        document: Document object or dictionary containing uuid, conversation_uuid, text, and metadata
    """
    # Handle Document object
    if isinstance(document, Document):
        metadata = document.metadata.copy()
        # Convert enum to string for JSON serialization
        if metadata.get('type'):
            metadata['type'] = metadata['type'].value if hasattr(metadata['type'], 'value') else str(metadata['type'])
            
        doc_dict = {
            'uuid': str(document.uuid),
            'conversation_uuid': document.conversation_uuid,
            'text': document.text,
            'metadata': metadata
        }
    else:
        # Handle dictionary input
        doc_dict = document.copy()
        if doc_dict.get('metadata', {}).get('type'):
            doc_dict['metadata']['type'] = (
                doc_dict['metadata']['type'].value 
                if hasattr(doc_dict['metadata']['type'], 'value') 
                else str(doc_dict['metadata']['type'])
            )
        doc_dict['uuid'] = str(doc_dict['uuid'])

    DocumentModel.create(**doc_dict)


def find_document_by_uuid(document_uuid: UUID) -> Optional[Document]:
    """
    Retrieve a document by its UUID
    
    Args:
        document_uuid: UUID of the document to find
            
    Returns:
        Document dictionary if found, None otherwise
    """
    try:
        doc = DocumentModel.get(DocumentModel.uuid == str(document_uuid))
        metadata = doc.metadata
        
        if parent_uuid := metadata.get('parent_document_uuid'):
            metadata['parent_document_uuid'] = UUID(parent_uuid)
            
        return Document(
            uuid=UUID(doc.uuid),
            conversation_uuid=doc.conversation_uuid,
            text=doc.text,
            metadata=metadata
        )
    except DocumentModel.DoesNotExist:
        return None


def find_documents_by_conversation(conversation_uuid: str) -> List[Document]:
    """
    Retrieve all documents for a given conversation
    
    Args:
        conversation_uuid: UUID of the conversation
            
    Returns:
        List of document dictionaries
    """
    query = DocumentModel.select().where(DocumentModel.conversation_uuid == conversation_uuid)
    
    documents = []
    for doc in query:
        metadata = doc.metadata
        if parent_uuid := metadata.get('parent_document_uuid'):
            metadata['parent_document_uuid'] = UUID(parent_uuid)
            
        documents.append(Document(
            uuid=UUID(doc.uuid),
            conversation_uuid=doc.conversation_uuid,
            text=doc.text,
            metadata=metadata
        ))
    
    return documents


