from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict
from uuid import UUID

from document.types import Document


class ActionStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


@dataclass
class ActionResult:
    """Result of an action performed by a tool"""
    result: str
    status: ActionStatus
    documents: List[Document] = field(default_factory=list)


@dataclass
class Action:
    """An action performed by a tool"""
    uuid: UUID
    name: str
    tool_uuid: UUID
    conversation_uuid: str
    payload: Dict
    result: str
    status: ActionStatus
    documents: List[Document] = field(default_factory=list)
