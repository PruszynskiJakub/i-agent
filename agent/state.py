from dataclasses import dataclass
from typing import List, Dict, Any

from db.message import find_messages_by_conversation, save_message
from message.utils import create_message
from db.action import find_actions_by_conversation
from db.document import find_documents_by_conversation
from document.types import Document
from tools.types import Action

from agent.types import Message


@dataclass(frozen=True)
class StepInfo:
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
    step_info: StepInfo
    understanding: str = ""

    def copy(self, **kwargs) -> 'AgentState':
        current_values = {
            'conversation_uuid': self.conversation_uuid,
            'messages': self.messages.copy(),
            'taken_actions': self.taken_actions.copy(),
            'documents': self.documents.copy(),
            'current_step': self.current_step,
            'max_steps': self.max_steps,
            'step_info': self.step_info,
            'understanding': self.understanding
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
        max_steps=2,
        step_info=StepInfo(
            overview="",
            tool="",
            tool_uuid="",
            tool_action="",
            tool_action_params={}
        ),
        understanding=""
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
        result=action_dict['result'],
        status=action_dict['status'],
        documents=action_dict.get('documents', []),
        step_description=action_dict.get('step_description', '')
    )
    
    return state.copy(taken_actions=[*state.taken_actions, action])


def add_documents(state: AgentState, documents: List[Document]) -> AgentState:
    return state.copy(documents=[*state.documents, *documents])

def should_continue(state: AgentState) -> bool:
    return state.current_step < state.max_steps

def update_step_info(state: AgentState, updates: Dict[str, Any]) -> AgentState:
    current_values = {
        'overview': state.step_info.overview,
        'tool': state.step_info.tool,
        'tool_uuid': state.step_info.tool_uuid,
        'tool_action': state.step_info.tool_action,
        'tool_action_params': state.step_info.tool_action_params
    }
    current_values.update(updates)
    return state.copy(step_info=StepInfo(**current_values))
