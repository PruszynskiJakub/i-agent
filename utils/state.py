from typing import List, Optional, Dict, Any

from db.message import save_message
from models.document import Document
from models.state import AgentState, AgentPhase, Task, TaskAction
from utils.message import create_message


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


def update_current_action(state: AgentState, action_updates: dict) -> AgentState:
    # Create a new TaskAction from the provided updates or update existing one
    if state.current_action is not None:
        new_action = state.current_action.model_copy(update=action_updates)
    else:
        new_action = TaskAction(**action_updates)
    new_state = state.copy(current_action=new_action)

    if state.current_task is not None:
        # Determine the action uuid to update: prefer the one from action_updates, or use current_action's uuid if available.
        action_uuid = action_updates.get("uuid")
        if action_uuid is None and state.current_action is not None:
            action_uuid = state.current_action.uuid

        # Update the actions list: if an action with the same uuid exists, replace it; otherwise, append the new action.
        found = False
        new_actions = []
        for act in state.current_task.actions:
            if getattr(act, "uuid", None) == action_uuid:
                new_actions.append(new_action)
                found = True
            else:
                new_actions.append(act)
        if not found:
            new_actions.append(new_action)

        # Update current_task with the new actions list.
        updated_task = state.current_task.model_copy(update={"actions": new_actions})
        new_state = new_state.copy(current_task=updated_task)

        # Also update the corresponding task in the tasks list.
        updated_tasks = []
        for task in state.tasks:
            if task.uuid == updated_task.uuid:
                updated_tasks.append(updated_task)
            else:
                updated_tasks.append(task.model_copy())
        new_state = new_state.copy(tasks=updated_tasks)

        # Persist changes to database
        from db.tasks import save_task
        save_task(updated_task)

    return new_state


def update_current_tool(state: AgentState, tool) -> AgentState:
    return state.copy(current_tool=tool)


def update_thoughts(state: AgentState, thoughts) -> AgentState:
    return state.copy(thoughts=thoughts)


def update_task(state: AgentState, task_uuid: str, updates: Dict[str, Any]) -> AgentState:
    """Update a task with persistence"""
    from db.tasks import save_task

    task = find_task(state, task_uuid)
    if task:
        updated_task = task.model_copy(update=updates)
        new_state = update_current_task(state, updated_task)

        # Persist to database
        save_task(updated_task)

        return new_state
    return state


def complete_task(state: AgentState, task_uuid: str) -> AgentState:
    """Mark a task as complete with persistence"""
    from db.tasks import update_task_status

    task = find_task(state, task_uuid)
    if task:
        updated_task = task.model_copy(update={"status": "done"})
        new_state = update_current_task(state, updated_task)

        # Persist to database
        update_task_status(task_uuid, "done")

        return new_state
    return state


def find_task(state: AgentState, task_uuid: str) -> Optional[Task]:
    # First try to find by UUID
    task = next((task for task in state.tasks if task.uuid == task_uuid), None)
    return task
