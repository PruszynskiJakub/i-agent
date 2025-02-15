from dataclasses import field
from enum import Enum
from typing import List, Dict, Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.document import Document
from models.message import Message


class AgentPhase(str, Enum):
    INTENT = "intent"
    PLAN = "plan"
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
    input_payload: Dict[str, Any] = field(default_factory=dict)
    output_documents: List[Document] = field(default_factory=list)
    step: int
    status: str # pending, done, failed

    model_config = ConfigDict(frozen=True)


class Task(BaseModel):
    uuid: str
    name: str
    description: str
    actions: List[TaskAction]
    status: str  # pending or done

    model_config = ConfigDict(frozen=True)


class AgentState(BaseModel):
    conversation_uuid: str
    messages: List[Message]
    tasks: List[Task]
    conversation_documents: List[Document]

    phase: AgentPhase
    current_step: int
    max_steps: int
    thoughts: Thoughts
    current_task: Optional[Task]
    current_action: Optional[TaskAction]
    current_tool: Optional[str]
    tool_dynamic_context: str

    @property
    def user_query(self) -> str:
        """Returns the content of the last user message"""
        for message in reversed(self.messages):
            if message.role == "user":
                return message.content
        return ""

    @property
    def assistant_response(self) -> str:
        """Returns the content of the last assistant message"""
        for message in reversed(self.messages):
            if message.role == "assistant":
                return message.content
        return ""

    model_config = ConfigDict(frozen=True)

    def copy(self, **kwargs) -> 'AgentState':
        return self.model_copy(update=kwargs)
