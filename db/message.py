import uuid
from datetime import datetime
from typing import List

from db.models import MessageModel
from agent.types import Message


def save_message(message: Message) -> None:
    """
    Save a message to the database
    
    Args:
        message: Message object to save
    """
    MessageModel.create(
        uuid=message.uuid,
        conversation_uuid=message.conversation_uuid,
        content=message.content,
        role=message.role,
        created_at=message.created_at
    )


def find_messages_by_conversation(conversation_uuid: str) -> List[Message]:
    """
    Find all messages in a conversation
    
    Args:
        conversation_uuid: Conversation UUID
            
    Returns:
        List of Message objects
    """
    query = MessageModel.select().where(
        MessageModel.conversation_uuid == conversation_uuid
    ).order_by(MessageModel.created_at)
    
    return [
        Message(
            uuid=msg.uuid,
            conversation_uuid=msg.conversation_uuid,
            content=msg.content,
            role=msg.role,
            created_at=msg.created_at
        ) for msg in query
    ]


def create_message(conversation_uuid: str, content: str, role: str) -> Message:
    """
    Create a new message without saving
    
    Args:
        conversation_uuid: UUID of the conversation
        content: Message content
        role: Message role (e.g., 'user', 'assistant')
            
    Returns:
        Created Message object
    """
    return Message(
        uuid=str(uuid.uuid4()),
        conversation_uuid=conversation_uuid,
        content=content,
        role=role,
        created_at=datetime.utcnow()
    )
