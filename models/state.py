from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import UUID
import enum

from models.action import ActionRecord
from models.message import Message
from models.document import Document

class AgentPhase(enum.Enum):
    BRAINSTORM = "brainstorm"
    PLAN = "plan"
    DEFINE = "define"
    DECIDE = "decide"
    EXECUTE = "execute"
    ANSWER = "answer"

@dataclass(frozen=True)
class ToolThought:
    """A single potential tool usage or action idea."""
    reason: str
    query: str
    tool_name: str

@dataclass(frozen=True)
class Thoughts:
    """Internal reasoning plus recommended tool candidates."""
    chain_of_thought: Optional[str]  # Hidden or partial reasoning text
    tool_candidates: List[ToolThought] = field(default_factory=list)

@dataclass(frozen=True)
class Interaction:
    """
    Represents the current (or latest) interaction step
    """
    overview: str
    tool: str
    tool_uuid: Optional[UUID]
    tool_action: str
    query: str
    payload: Dict[str, Any]
    status: str = "PENDING"

@dataclass(frozen=True)
class AgentState:
    conversation_uuid: str
    current_step: int
    max_steps: int
    phase: AgentPhase
    messages: List[Message]
    action_history: List[ActionRecord]
    interaction: Optional[Interaction]
    thoughts: Optional[Thoughts] = None
    documents: List[Document] = field(default_factory=list)
    dynamic_context: str = ""

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
            'action_history': self.action_history.copy(),
            'documents': self.documents.copy(),
            'current_step': self.current_step,
            'max_steps': self.max_steps,
            'phase': self.phase,
            'interaction': self.interaction,
            'thoughts': self.thoughts,
            'dynamic_context': self.dynamic_context,
        }
        current_values.update(kwargs)
        return AgentState(**current_values)
