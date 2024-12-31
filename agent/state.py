from dataclasses import dataclass
from typing import List

from db.message import find_messages_by_conversation, create_message
from document.types import Document
from models.action import Action

from models.message import Message


@dataclass(frozen=True)
class AgentState:
    conversation_uuid: str
    messages: List[Message]
    taken_actions: List[Action]
    documents: List[Document]
    current_step: int
    max_steps: int

    def copy(self, **kwargs) -> 'AgentState':
        current_values = {
            'conversation_uuid': self.conversation_uuid,
            'messages': self.messages.copy(),
            'taken_actions': self.taken_actions.copy(),
            'documents': self.documents.copy(),
            'current_step': self.current_step,
            'max_steps': self.max_steps
        }
        current_values.update(kwargs)
        return AgentState(**current_values)


def create_or_restore_state(conversation_uuid: str) -> AgentState:
    return AgentState(
        conversation_uuid=conversation_uuid,
        messages=find_messages_by_conversation(conversation_uuid),
        taken_actions=[],
        documents=[],
        current_step=0,
        max_steps=1
    )


def increment_current_step(state: AgentState) -> AgentState:
    return state.copy(current_step=state.current_step + 1)


def add_message(state: AgentState, content, role) -> AgentState:
    message = create_message(state.conversation_uuid, content, role)
    return state.copy(messages=[*state.messages, message])


def add_taken_action(state: AgentState, action: Action) -> AgentState:
    return state.copy(taken_actions=[*state.taken_actions, action])


def add_documents(state: AgentState, documents: List[Document]) -> AgentState:
    return state.copy(documents=[*state.documents, *documents])

def should_continue(state: AgentState) -> bool:
    return state.current_step < state.max_steps