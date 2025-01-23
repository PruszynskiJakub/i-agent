from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import UUID
import enum
from message.types import Message
from document.types import Document
from db.message import find_messages_by_conversation, save_message
from db.document import find_documents_by_conversation
from message.utils import create_message

class AgentPhase(enum.Enum):
    PLAN = "plan"
    DEFINE = "define" 
    EXECUTE = "execute"
    ANSWER = "answer"

@dataclass(frozen=True)
class ToolCandidate:
    """A single potential tool usage or action idea."""
    tool_name: str
    reason: str
    confidence: float = 0.0

@dataclass(frozen=True)
class Thoughts:
    """Internal reasoning plus recommended tool candidates."""
    chain_of_thought: Optional[str]  # Hidden or partial reasoning text
    tool_candidates: List[ToolCandidate] = field(default_factory=list)

@dataclass(frozen=True)
class Decision:
    """High-level plan or next step the agent wants to take."""
    overview: str
    chosen_tool: Optional[str] = None
    chosen_action: Optional[str] = None

@dataclass(frozen=True)
class ActionRecord:
    """A record of an executed tool action."""
    name: str  # e.g. "complete_task", "create_transaction"
    tool: str
    tool_uuid: Optional[UUID]
    status: str  # "SUCCESS" or "ERROR"
    input_payload: Dict[str, Any]
    output_documents: List[Document]
    step_description: str

@dataclass(frozen=True)
class Interaction:
    """
    Represents the current (or latest) interaction step
    """
    overview: str
    tool: str
    tool_uuid: UUID
    tool_action: str
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
    decision: Optional[Decision] = None
    documents: List[Document] = field(default_factory=list)
    dynamic_context: str = ""
    final_answer: Optional[str] = None

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
            'decision': self.decision,
            'dynamic_context': self.dynamic_context,
            'final_answer': self.final_answer
        }
        current_values.update(kwargs)
        return AgentState(**current_values)

def create_or_restore_state(conversation_uuid: str) -> AgentState:
    return AgentState(
        conversation_uuid=conversation_uuid,
        messages=find_messages_by_conversation(conversation_uuid),
        action_history=[],  # Will be populated from actions DB
        documents=find_documents_by_conversation(conversation_uuid),
        current_step=0,
        max_steps=4,
        phase=AgentPhase.PLAN,
        interaction=None,
        thoughts=None,
        decision=None,
        dynamic_context="",
        final_answer=None
    )


def increment_current_step(state: AgentState) -> AgentState:
    return state.copy(current_step=state.current_step + 1)


def add_message(state: AgentState, content, role) -> AgentState:
    message = create_message(state.conversation_uuid, content, role)
    save_message(message)
    return state.copy(messages=[*state.messages, message])


def add_taken_action(state: AgentState, action_dict: Dict[str, Any]) -> AgentState:
    """
    Create an Action in the database and add it to the state
    
    Args:
        state: Current agent state
        action_dict: Dictionary containing action data
            
    Returns:
        Updated AgentState with new action
    """
    from db.action import create_action
    
    action = create_action(
        conversation_uuid=state.conversation_uuid,
        name=action_dict['name'],
        tool_uuid=action_dict['tool_uuid'],
        payload=action_dict['payload'],
        status=action_dict['status'],
        documents=action_dict.get('documents', []),
        step_description=action_dict.get('step_description', '')
    )
    
    return state.copy(taken_actions=[*state.taken_actions, action])


def add_documents(state: AgentState, documents: List[Document]) -> AgentState:
    return state.copy(documents=[*state.documents, *documents])

def should_continue(state: AgentState) -> bool:
    return state.current_step < state.max_steps

def update_interaction(state: AgentState, updates: Dict[str, Any]) -> AgentState:
    current_values = {
        'overview': state.interaction.overview,
        'tool': state.interaction.tool,
        'tool_uuid': state.interaction.tool_uuid,
        'tool_action': state.interaction.tool_action,
        'payload': state.interaction.payload
    }
    current_values.update(updates)
    return state.copy(interaction=Interaction(**current_values))