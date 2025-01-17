from typing import Dict, Any
from tools.types import ActionResult, ActionStatus
from todoist import todoist_client

async def add_todos(params: Dict[str, Any], span) -> str:
    """Add todo items to the Inbox project"""
    try:
        # Get the todos from params
        todos = params.get("todos", [])
        if not todos:
            return "No todos provided"

        # Add each todo to the Inbox project
        for todo in todos:
            task = todoist_client.add_task(
                content=todo,
                project_id="2334150459"  # Inbox project ID
            )
            
        return "Successfully added todos to Inbox"
        
    except Exception as error:
        return f"Failed to add todos: {str(error)}"
