import uuid
from datetime import datetime
from message.types import Message


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
