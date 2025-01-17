from typing import List, Optional, Dict, Any
from document.types import Document
from uuid import UUID
import json

from db import connection, execute


def save_document(document: Document | Dict[str, Any]) -> None:
    """
    Save a document to the database
    
    Args:
        document: Document object or dictionary containing uuid, conversation_uuid, text, and metadata
    """
    # Convert Document object to dict if needed
    if isinstance(document, Document):
        metadata = document.metadata.copy()
        # Convert enum to string for JSON serialization
        if 'type' in metadata:
            metadata['type'] = metadata['type'].value if hasattr(metadata['type'], 'value') else str(metadata['type'])
            
        doc_dict = {
            'uuid': document.uuid,
            'conversation_uuid': document.conversation_uuid,
            'text': document.text,
            'metadata': metadata
        }
    else:
        doc_dict = document
    query = """
        INSERT INTO documents (uuid, conversation_uuid, text, metadata)
        VALUES (?, ?, ?, ?)
    """
    execute(query, (
        str(doc_dict['uuid']),
        doc_dict['conversation_uuid'],
        doc_dict['text'],
        json.dumps(doc_dict['metadata'])
    ))


def find_document_by_uuid(document_uuid: UUID) -> Optional[Document]:
    """
    Retrieve a document by its UUID
    
    Args:
        document_uuid: UUID of the document to find
            
    Returns:
        Document dictionary if found, None otherwise
    """
    query = """
        SELECT uuid, conversation_uuid, text, metadata
        FROM documents WHERE uuid = ?
    """
    rows = execute(query, (str(document_uuid),))
    row = rows[0]
    
    if not row:
        return None

    metadata = json.loads(row[3])
    
    # Convert parent_document_uuid back to UUID if it exists
    if parent_uuid := metadata.get('parent_document_uuid'):
        metadata['parent_document_uuid'] = UUID(parent_uuid)

    return Document(
        uuid=UUID(row[0]),
        conversation_uuid=row[1],
        text=row[2],
        metadata=metadata
    )


def find_documents_by_conversation(conversation_uuid: str) -> List[Document]:
    """
    Retrieve all documents for a given conversation
    
    Args:
        conversation_uuid: UUID of the conversation
            
    Returns:
        List of document dictionaries
    """
    query = """
        SELECT uuid, conversation_uuid, text, metadata
        FROM documents WHERE conversation_uuid = ?
    """
    rows = execute(query, (conversation_uuid,))
    
    documents = []
    for row in rows:
        if row[0] is None:
            continue
            
        metadata = json.loads(row[3])
        if parent_uuid := metadata.get('parent_document_uuid'):
            metadata['parent_document_uuid'] = UUID(parent_uuid)
            
        documents.append(Document(
            uuid=UUID(row[0]),
            conversation_uuid=row[1],
            text=row[2],
            metadata=metadata
        ))
    
    return documents


def create_document(conversation_uuid: str, text: str, metadata: Dict[str, Any]) -> Document:
    """
    Create and save a new document
    
    Args:
        conversation_uuid: UUID of the conversation
        text: Document text content
        metadata: Document metadata
            
    Returns:
        Created document dictionary
    """
    document = Document(
        uuid=UUID(),
        conversation_uuid=conversation_uuid,
        text=text,
        metadata=metadata
    )
    
    save_document(document.__dict__)
    return document

def ensure_document_table() -> None:
    """Ensure the documents table exists in the database"""
    query = """
        CREATE TABLE IF NOT EXISTS documents (
            uuid TEXT PRIMARY KEY,
            conversation_uuid TEXT NOT NULL,
            text TEXT NOT NULL,
            metadata TEXT NOT NULL
        )
    """
    execute(query)

ensure_document_table()
