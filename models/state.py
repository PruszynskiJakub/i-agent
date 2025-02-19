from dataclasses import field
from enum import Enum
from typing import List, Dict, Any, Optional

from pydantic import ConfigDict, BaseModel

from models.document import Document


class AgentPhase(str, Enum):
    INTENT = "intent"
    BLUEPRINT = "blueprint"
    DEFINE = "define"
    DECIDE = "decide"
    EXECUTE = "execute"
    ANSWER = "answer"


class ToolThought(BaseModel):
    """A single potential tool usage or action idea."""
    query: str
    tool_name: str

    model_config = ConfigDict(frozen=True)


class Thoughts(BaseModel):
    """Internal reasoning plus recommended tool candidates."""
    tool_thoughts: List[ToolThought] = field(default_factory=list)
    user_intent: str = ""

    model_config = ConfigDict(frozen=True)


class TaskAction(BaseModel):
    uuid: str
    name: str
    tool_uuid: str
    task_uuid: str
    tool_action: str
    input_payload: Dict[str, Any] = field(default_factory=dict)
    output_documents: List[Document] = field(default_factory=list)
    step: int
    status: str  # pending, done, failed

    model_config = ConfigDict(frozen=True)


class Task(BaseModel):
    uuid: str
    name: str
    description: str
    actions: List[TaskAction]
    status: str  # pending or done
    conversation_uuid: Optional[str] = None

    model_config = ConfigDict(frozen=True)
