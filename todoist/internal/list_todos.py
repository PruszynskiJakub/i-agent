from typing import List, Optional
from document.types import Document 
from document.utils import create_document
from todoist import todoist_client

async def list_todos(params: dict, span) -> Document:
    """
    List todos based on provided filters (project, label, section, or specific ids)
    Returns a Document containing the formatted task list
    """
    try:
        # Extract filter parameters
        project_id = params.get("project_id")
        label = params.get("label")
        section_id = params.get("section_id")
        task_ids = params.get("ids", [])

        # Get tasks with filters
        tasks = todoist_client.get_tasks(
            project_id=project_id,
            label=label,
            section_id=section_id,
            ids=task_ids
        )

        # Format tasks into readable text
        formatted_tasks = []
        for task in tasks:
            due_str = f" (Due: {task.due.string})" if task.due else ""
            priority_str = f" [P{task.priority}]" if task.priority > 1 else ""
            labels_str = f" #{',#'.join(task.labels)}" if task.labels else ""
            
            formatted_tasks.append(
                f"- {task.content}{priority_str}{due_str}{labels_str}"
            )

        content = "\n".join(formatted_tasks) if formatted_tasks else "No tasks found"
        
        return create_document(
            content=content,
            metadata={
                "task_count": len(formatted_tasks),
                "filters": {
                    "project_id": project_id,
                    "label": label,
                    "section_id": section_id,
                    "ids": task_ids
                }
            }
        )

    except Exception as e:
        raise Exception(f"Error listing todos: {str(e)}")
