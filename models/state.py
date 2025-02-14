import enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import UUID

from models.document import Document
from models.message import Message


class AgentPhase(enum.Enum):
    INTENT = "intent"
    PLAN = "plan"
    DEFINE = "define"
    DECIDE = "decide"
    EXECUTE = "execute"
    ANSWER = "answer"


@dataclass(frozen=True)
class ToolThought:
    """A single potential tool usage or action idea."""
    query: str
    tool_name: str


@dataclass(frozen=True)
class Thoughts:
    """Internal reasoning plus recommended tool candidates."""
    tool_thoughts: List[ToolThought] = field(default_factory=list)
    user_intent: str = ""


@dataclass(frozen=True)
class Action:
    uuid: str
    name: str
    tool_name: str
    tool_uuid: Optional[UUID]
    input_payload: Dict[str, Any]
    output_documents: List[Document]

@dataclass(frozen=True)
class Task:
    uuid: str
    name: str
    description: str
    actions: List[Action]
    status: str  # pending or done


@dataclass(frozen=True)
class AgentState:
    conversation_uuid: str
    messages: List[Message]
    tasks: List[Task]
    message_documents: List[Document]

    phase: AgentPhase
    current_step: int
    max_steps: int
    current_task: Optional[Task]
    current_action: Optional[Action]
    thoughts: Thoughts
    dynamic_context: str

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

    def copy(self, **kwargs) -> 'AgentState':
        current_values = {
            'conversation_uuid': self.conversation_uuid,
            'messages': self.messages.copy(),
            'tasks': self.tasks.copy(),
            'message_documents': self.message_documents.copy(),
            'current_step': self.current_step,
            'max_steps': self.max_steps,
            'phase': self.phase,
            'current_task': self.current_task,
            'current_action': self.current_action,
            'thoughts': self.thoughts,
            'dynamic_context': self.dynamic_context,
        }
        current_values.update(kwargs)
        return AgentState(**current_values)
