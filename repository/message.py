from datetime import datetime
import uuid
from typing import List, Optional

from model.message import Message
from repository.database import Database

class MessageRepository:
    """Repository for managing Message entities in the database"""

    def __init__(self, database: Database):
        self.db = database
        self._ensure_table()

    def _ensure_table(self) -> None:
        """Ensure the messages table exists in the database"""
        query = '''
            CREATE TABLE IF NOT EXISTS messages (
                uuid TEXT PRIMARY KEY,
                conversation_uuid TEXT NOT NULL,
                content TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        self.db.execute(query)

    def save(self, message: Message) -> None:
        """
        Save a message to the database
        
        Args:
            message: Message object to save
        """
        query = '''
            INSERT INTO messages (uuid, conversation_uuid, content, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.db.execute(query, (
            message.uuid,
            message.conversation_uuid,
            message.content,
            message.role,
            message.created_at.isoformat()
        ))

    def find_by_uuid(self, uuid: str) -> Optional[Message]:
        """
        Find a message by its UUID
        
        Args:
            uuid: Message UUID
            
        Returns:
            Message object if found, None otherwise
        """
        query = 'SELECT uuid, conversation_uuid, content, role, created_at FROM messages WHERE uuid = ?'
        result = self.db.execute(query, (uuid,))
        
        if not result:
            return None
            
        row = result[0]
        return Message(
            uuid=row[0],
            conversation_uuid=row[1],
            content=row[2],
            role=row[3],
            created_at=datetime.fromisoformat(row[4])
        )

    def find_by_conversation(self, conversation_uuid: str) -> List[Message]:
        """
        Find all messages in a conversation
        
        Args:
            conversation_uuid: Conversation UUID
            
        Returns:
            List of Message objects
        """
        query = '''
            SELECT uuid, conversation_uuid, content, role, created_at 
            FROM messages 
            WHERE conversation_uuid = ?
            ORDER BY created_at
        '''
        results = self.db.execute(query, (conversation_uuid,))
        
        return [
            Message(
                uuid=row[0],
                conversation_uuid=row[1],
                content=row[2],
                role=row[3],
                created_at=datetime.fromisoformat(row[4])
            )
            for row in results
        ]

    def create(self, conversation_uuid: str, content: str, role: str) -> Message:
        """
        Create and save a new message
        
        Args:
            conversation_uuid: UUID of the conversation
            content: Message content
            role: Message role (e.g., 'user', 'assistant')
            
        Returns:
            Created Message object
        """
        message = Message(
            uuid=str(uuid.uuid4()),
            conversation_uuid=conversation_uuid,
            content=content,
            role=role,
            created_at=datetime.utcnow()
        )
        
        self.save(message)
        return message 