from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from db.message import find_messages_by_conversation, save_message
from message.utils import create_message
from db.action import find_actions_by_conversation
from db.document import find_documents_by_conversation
from document.types import Document
from tools.types import Action

from message.types import Message


@dataclass(frozen=True)
class ToolThought:
    reason: str
    tool: str
    query: str

@dataclass(frozen=True)
class Thoughts:
    tools: List[ToolThought]

@dataclass(frozen=True)
class Interaction:
    overview: str
    tool: str
    tool_uuid: str
    tool_action: str
    tool_action_params: Dict[str, Any]


@dataclass(frozen=True)
class AgentState:
    conversation_uuid: str
    messages: List[Message]
    taken_actions: List[Action]
    documents: List[Document]
    current_step: int
    max_steps: int
    interaction: Interaction
    thoughts: Optional[Thoughts] = None

    def copy(self, **kwargs) -> 'AgentState':
        current_values = {
            'conversation_uuid': self.conversation_uuid,
            'messages': self.messages.copy(),
            'taken_actions': self.taken_actions.copy(),
            'documents': self.documents.copy(),
            'current_step': self.current_step,
            'max_steps': self.max_steps,
            'interaction': self.interaction,
            'thoughts': self.thoughts
        }
        current_values.update(kwargs)
        return AgentState(**current_values)


def create_or_restore_state(conversation_uuid: str) -> AgentState:
    return AgentState(
        conversation_uuid=conversation_uuid,
        messages=find_messages_by_conversation(conversation_uuid),
        taken_actions=find_actions_by_conversation(conversation_uuid),
        documents=find_documents_by_conversation(conversation_uuid),
        current_step=0,
        max_steps=4,
        interaction=Interaction(
            overview="",
            tool="",
            tool_uuid="",
            tool_action="",
            tool_action_params={}
        ),
        thoughts=None
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
        'tool_action_params': state.interaction.tool_action_params
    }
    current_values.update(updates)
    return state.copy(interaction=Interaction(**current_values))
