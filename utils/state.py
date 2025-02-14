from typing import List, Dict, Any, Optional

from db.conversation import load_conversation_documents
from db.message import find_messages_by_conversation, save_message
from models.document import Document
from models.state import AgentState, AgentPhase, Thoughts
from utils.message import create_message


def create_or_restore_state(conversation_uuid: str) -> AgentState:
    return AgentState(
        conversation_uuid=conversation_uuid,
        messages=find_messages_by_conversation(conversation_uuid),
        tasks=[],
        conversation_documents=load_conversation_documents(conversation_uuid),
        current_step=0,
        max_steps=4,
        phase=AgentPhase.INTENT,
        current_task=None,
        current_action=None,
        thoughts=Thoughts(),
        dynamic_context=""
    )


def complete_interaction(state: AgentState) -> AgentState:
    return state.copy(
        current_step=state.current_step + 1,
        dynamic_context=""
    )


def add_message(state: AgentState, content, role) -> AgentState:
    message = create_message(state.conversation_uuid, content, role)
    save_message(message)
    return state.copy(messages=[*state.messages, message])


def add_documents(state: AgentState, documents: List[Document]) -> AgentState:
    return state.copy(documents=[*state.conversation_documents, *documents])


def update_phase(state: AgentState, new_phase: AgentPhase) -> AgentState:
    return state.copy(phase=new_phase)


def set_dynamic_context(state: AgentState, context: str) -> AgentState:
    return state.copy(dynamic_context=context)


def update_current_task(state: AgentState, task) -> AgentState:
    return state.copy(current_task=task)


def update_tasks(state: AgentState, tasks) -> AgentState:
    return state.copy(tasks=tasks)


def update_current_action(state: AgentState, action) -> AgentState:
    return state.copy(current_action=action)


def update_thoughts(state: AgentState, thoughts) -> AgentState:
    return state.copy(thoughts=thoughts)


def find_task(state: AgentState, task_id: str) -> Optional[Task]:
    """
    Find a task in state.tasks by UUID first, then by name if UUID search fails.
    
    Args:
        state: Current agent state
        task_id: UUID or name of the task to find
        
    Returns:
        Task if found, None otherwise
    """
    # First try to find by UUID
    task = next((task for task in state.tasks if task.uuid == task_id), None)
    
    # If not found by UUID, try to find by name
    if task is None:
        task = next((task for task in state.tasks if task.name == task_id), None)
        
    return task


def should_continue(state: AgentState) -> bool:
    return state.current_step < state.max_steps
