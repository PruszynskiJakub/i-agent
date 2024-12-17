from typing import List, Optional
import json
from uuid import UUID

from app.core.model.document import Document, DocumentMetadata
from app.core.infrastructure.repository.database import Database


class DocumentRepository:
    """Repository for managing Document entities in the database"""

    def __init__(self, database: Database):
        self.db = database
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Create the necessary tables if they don't exist"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                uuid TEXT PRIMARY KEY,
                conversation_uuid TEXT NOT NULL,
                text TEXT NOT NULL,
                metadata TEXT NOT NULL
            )
        """)

    def save(self, document: Document) -> None:
        """Save a document to the database"""
        self.db.execute("""
            INSERT INTO documents (uuid, conversation_uuid, text, metadata)
            VALUES (?, ?, ?, ?)
        """, (
            str(document['uuid']),
            document['conversation_uuid'],
            document['text'],
            json.dumps(document['metadata'])
        ))

    def find_by_id(self, uuid: UUID) -> Optional[Document]:
        """Retrieve a document by its UUID"""
        result = self.db.execute("""
            SELECT uuid, conversation_uuid, text, metadata
            FROM documents WHERE uuid = ?
        """, (str(uuid),))
        
        if not result:
            return None

        doc = result[0]
        metadata = json.loads(doc[3])
        
        # Convert parent_document_uuid back to UUID if it exists
        if parent_uuid := metadata.get('parent_document_uuid'):
            metadata['parent_document_uuid'] = UUID(parent_uuid)

        return Document(
            uuid=UUID(doc[0]),
            conversation_uuid=doc[1],
            text=doc[2],
            metadata=metadata
        )

    def find_by_conversation(self, conversation_uuid: str) -> List[Document]:
        """Retrieve all documents for a given conversation"""
        docs = self.db.execute("""
            SELECT uuid FROM documents WHERE conversation_uuid = ?
        """, (conversation_uuid,))
        
        return [self.find_by_id(UUID(doc[0])) for doc in docs] if docs else [] 