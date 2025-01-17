from typing import Dict, Any
from tools.types import ActionResult, ActionStatus
from todoist import todoist_client

async def add_todos(params: Dict[str, Any], span) -> str:
    """Add todo items with optional metadata"""
    try:
        todos = params.get("todos", [])
        if not todos:
            return "No todos provided"

        for todo in todos:
            if not todo.get("title"):
                continue

            task_args = {
                "content": todo["title"],
                "project_id": todo.get("projectId", "2334150459"),  # Default to Inbox if not specified
            }

            # Add optional parameters if present
            if todo.get("description"):
                task_args["description"] = todo["description"]
            if todo.get("priority"):
                task_args["priority"] = max(1, min(4, todo["priority"]))  # Clamp between 1-4
            if todo.get("labelIds"):
                task_args["label_ids"] = todo["labelIds"]
            if todo.get("dueDate"):
                task_args["due_date"] = todo["dueDate"]

            task = todoist_client.add_task(**task_args)

        return "Successfully added todos"
        
    except Exception as error:
        return f"Failed to add todos: {str(error)}"
