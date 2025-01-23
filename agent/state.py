from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from uuid import UUID
import enum
from message.types import Message
from document.types import Document
from db.message import find_messages_by_conversation, save_message
from db.document import find_documents_by_conversation
from db.action import find_action_records_by_conversation
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
    query: str

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
    tool_uuid: Optional[UUID]
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
        action_history=find_action_records_by_conversation(conversation_uuid),
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


def complete_interaction(state: AgentState) -> AgentState:
    """
    Increments current_step by 1 and clears interaction and dynamic_context.

    Args:
        state: Current agent state

    Returns:
        Updated AgentState with incremented current_step and cleared fields
    """
    return state.copy(
        current_step=state.current_step + 1,
        interaction=None,
        dynamic_context=""
    )


def add_message(state: AgentState, content, role) -> AgentState:
    message = create_message(state.conversation_uuid, content, role)
    save_message(message)
    return state.copy(messages=[*state.messages, message])


def record_action(state: AgentState, action_dict: Dict[str, Any]) -> AgentState:
    """
    Create an ActionRecord in the database and add it to the state's action_history

    Args:
        state: Current agent state
        action_dict: Dictionary containing action data

    Returns:
        Updated AgentState with new action record in action_history
    """
    from db.action import save_action_record

    action_record = save_action_record(
        conversation_uuid=state.conversation_uuid,
        name=action_dict['name'],
        tool=action_dict.get('tool', ''),
        tool_uuid=action_dict.get('tool_uuid'),
        input_payload=action_dict['payload'],
        status=action_dict['status'],
        output_documents=action_dict.get('documents', []),
        step_description=action_dict.get('step_description', '')
    )

    return state.copy(action_history=state.action_history + [action_record])


def add_documents(state: AgentState, documents: List[Document]) -> AgentState:
    return state.copy(documents=[*state.documents, *documents])

def update_phase(state: AgentState, new_phase: AgentPhase) -> AgentState:
    """
    Update the phase of the AgentState

    Args:
        state: Current agent state
        new_phase: The new phase to set

    Returns:
        Updated AgentState with new phase
    """
    return state.copy(phase=new_phase)

def set_dynamic_context(state: AgentState, context: str) -> AgentState:
    """
    Set the dynamic context in the AgentState

    Args:
        state: Current agent state
        context: New dynamic context string

    Returns:
        Updated AgentState with updated dynamic_context
    """
    return state.copy(dynamic_context=context)

def should_interact(state: AgentState) -> bool:
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

def new_interaction(state: AgentState) -> AgentState:
    """
    Create a new empty Interaction object with PENDING status and update the state with it.

    Args:
        state: Current agent state

    Returns:
        Updated AgentState with new empty interaction
    """
    interaction = Interaction(
        overview="",
        tool="",
        tool_uuid=None,
        tool_action="",
        payload={},
        status="PENDING"
    )
    return state.copy(interaction=interaction)
