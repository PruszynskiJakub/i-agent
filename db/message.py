import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from db import connection, execute
from types.message import Message


def save_message(message: Message) -> None:
    """
    Save a message to the database
    
    Args:
        message: Message object to save
    """
    query = '''
        INSERT INTO messages (uuid, conversation_uuid, content, role, created_at)
        VALUES (?, ?, ?, ?, ?)
    '''
    execute(query, (
        message.uuid,
        message.conversation_uuid,
        message.content,
        message.role,
        message.created_at.isoformat()
    ))


def _row_to_message(row: Tuple) -> Message:
    """Convert a database row to a Message object"""
    return Message(
        uuid=row[0],
        conversation_uuid=row[1],
        content=row[2],
        role=row[3],
        created_at=datetime.fromisoformat(row[4])
    )


def find_messages_by_conversation(conversation_uuid: str) -> List[Message]:
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
    rows = execute(query, (conversation_uuid,))
    return [_row_to_message(row) for row in rows]


def create_message(conversation_uuid: str, content: str, role: str) -> Message:
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

    save_message(message)
    return message


def ensure_message_table() -> None:
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
    execute(query)


ensure_message_table()