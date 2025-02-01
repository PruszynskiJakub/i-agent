from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    Represents a message in a conversation

    Attributes:
        uuid: Unique identifier for the message
        conversation_uuid: UUID of the conversation this message belongs to
        content: The actual message content
        role: Role of the message sender (user or assistant)
        created_at: Timestamp when the message was created
    """
    uuid: str = Field(..., description="Unique identifier for the message")
    conversation_uuid: str = Field(..., description="UUID of the conversation")
    content: str = Field(..., description="Message content")
    role: Literal["user", "assistant"] = Field(..., description="Role of the message sender")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Message creation timestamp")
