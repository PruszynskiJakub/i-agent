from typing import List, Optional

from agent.state import AgentState, Task
from models.document import Document


def add_documents(state: AgentState, documents: List[Document]) -> AgentState:
    return state.copy(documents=[*state.conversation_documents, *documents])


def complete_task(state: AgentState, task_uuid: str) -> AgentState:
    """Mark a task as complete with persistence"""
    from db.tasks import update_task_status

    task = find_task(state, task_uuid)
    if task:
        updated_task = task.model_copy(update={"status": "done"})
        new_state = state.update_current_task(updated_task)

        # Persist to database
        update_task_status(task_uuid, "done")

        return new_state
    return state


def find_task(state: AgentState, task_uuid: str) -> Optional[Task]:
    # First try to find by UUID
    task = next((task for task in state.tasks if task.uuid == task_uuid), None)
    return task
