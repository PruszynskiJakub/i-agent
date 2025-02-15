from typing import List, Optional

from db.conversation import load_conversation_documents
from db.message import find_messages_by_conversation, save_message
from models.document import Document
from models.state import AgentState, AgentPhase, Thoughts, Task
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
        tool_dynamic_context=""
    )


def complete_thinking_session(state: AgentState) -> AgentState:
    return state.copy(
        current_step=state.current_step + 1,
        tool_dynamic_context="",
        current_task=None,
        current_action=None,
        current_tool=None,
    )


def add_message(state: AgentState, content, role) -> AgentState:
    message = create_message(state.conversation_uuid, content, role)
    save_message(message)
    return state.copy(messages=[*state.messages, message])


def add_documents(state: AgentState, documents: List[Document]) -> AgentState:
    return state.copy(documents=[*state.conversation_documents, *documents])


def update_phase(state: AgentState, new_phase: AgentPhase) -> AgentState:
    return state.copy(phase=new_phase)


def set__tool_dynamic_context(state: AgentState, context: str) -> AgentState:
    return state.copy(tool_dynamic_context=context)


def update_current_task(state: AgentState, task) -> AgentState:
    return state.copy(current_task=task)


def update_tasks(state: AgentState, tasks) -> AgentState:
    return state.copy(tasks=tasks)


def update_current_action(state: AgentState, action) -> AgentState:
    return state.copy(current_action=action)

def update_current_tool(state: AgentState, tool) -> AgentState:
    return state.copy(current_tool=tool)


def update_thoughts(state: AgentState, thoughts) -> AgentState:
    return state.copy(thoughts=thoughts)


def find_task(state: AgentState, task_uuid: str, task_name: str) -> Optional[Task]:
    # First try to find by UUID
    task = next((task for task in state.tasks if task.uuid == task_uuid), None)

    # If not found by UUID, try to find by name
    if task is None:
        task = next((task for task in state.tasks if task.name == task_name), None)

    return task


def should_continue(state: AgentState) -> bool:
    return state.current_step < state.max_steps
