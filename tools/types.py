from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict
from uuid import UUID

from document.types import Document




@dataclass
class Action:
    """An action performed by a tool"""
    uuid: UUID
    name: str
    tool_uuid: UUID
    conversation_uuid: str
    payload: Dict
    status: str
    documents: List[Document] = field(default_factory=list)
    step_description: str = ""
