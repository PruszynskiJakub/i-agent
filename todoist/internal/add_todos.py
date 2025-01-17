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
            if todo.get("labels"):
                task_args["labels"] = todo["labels"]  # Using label names instead of IDs
            
            # Handle due date options
            if todo.get("dueString"):
                task_args["due_string"] = todo["dueString"]
                if todo.get("dueLang"):
                    task_args["due_lang"] = todo["dueLang"]
            elif todo.get("dueDate"):
                task_args["due_date"] = todo["dueDate"]
            
            # Handle duration if specified
            if todo.get("duration") and todo.get("durationUnit"):
                task_args["duration"] = todo["duration"]
                task_args["duration_unit"] = todo["durationUnit"]

            task = todoist_client.add_task(**task_args)

        return "Successfully added todos"
        
    except Exception as error:
        return f"Failed to add todos: {str(error)}"
