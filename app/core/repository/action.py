from typing import List, Optional
import json
from uuid import UUID

from app.core.model.action import Action, ActionStatus
from app.core.repository.database import Database
from app.core.repository.document import DocumentRepository


class ActionRepository:
    """Repository for managing Action entities in the database"""

    def __init__(self, database: Database):
        self.db = database
        self.document_repository = DocumentRepository(database)
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        """Create the necessary tables if they don't exist"""
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS actions (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                tool_uuid TEXT NOT NULL,
                payload TEXT NOT NULL,
                result TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)
        
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS action_documents (
                action_uuid TEXT,
                document_uuid TEXT,
                FOREIGN KEY (action_uuid) REFERENCES actions (uuid),
                FOREIGN KEY (document_uuid) REFERENCES documents (uuid),
                PRIMARY KEY (action_uuid, document_uuid)
            )
        """)

    def save(self, action: Action) -> None:
        """Save an action and its associated documents to the database"""
        # Save the action
        self.db.execute("""
            INSERT INTO actions (uuid, name, tool_uuid, payload, result, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(action.uuid),
            action.name,
            str(action.tool_uuid),
            json.dumps(action.payload),
            action.result,
            action.status.value
        ))

        # Save associated documents and their relationships
        for document in action.documents:
            self.document_repository.save(document)
            self.db.execute("""
                INSERT INTO action_documents (action_uuid, document_uuid)
                VALUES (?, ?)
            """, (str(action.uuid), str(document.uuid)))

    def find_by_id(self, uuid: UUID) -> Optional[Action]:
        """Retrieve an action by its UUID"""
        result = self.db.execute("""
            SELECT uuid, name, tool_uuid, payload, result, status
            FROM actions WHERE uuid = ?
        """, (str(uuid),))

        if not result:
            return None

        action_data = result[0]
        
        # Get associated documents
        doc_results = self.db.execute("""
            SELECT document_uuid FROM action_documents
            WHERE action_uuid = ?
        """, (str(uuid),))
        
        documents = []
        if doc_results:
            documents = [
                self.document_repository.find_by_id(UUID(doc[0]))
                for doc in doc_results
            ]

        return Action(
            uuid=UUID(action_data[0]),
            name=action_data[1],
            tool_uuid=UUID(action_data[2]),
            payload=json.loads(action_data[3]),
            result=action_data[4],
            status=ActionStatus(action_data[5]),
            documents=documents
        )

    def find_by_tool(self, tool_uuid: UUID) -> List[Action]:
        """Retrieve all actions for a given tool"""
        actions = self.db.execute("""
            SELECT uuid FROM actions WHERE tool_uuid = ?
        """, (str(tool_uuid),))
        
        return [self.find_by_id(UUID(action[0])) for action in actions] if actions else [] 