from typing import Any, Dict, List
from uuid import UUID

from todoist.service import execute_todoist
from ynab.service import execute_ynab


def get_tools():
    return [
        {
            "uuid": UUID("a3bb189e-8bf9-4c8b-9beb-5de10a41cf62"),
            "name": "ynab",
            "description": "responsible for managing budget, transactions etc., available only on direct request",
            "instructions": {
                "add_transaction": """
                {
                    "params": {
                        "transactions": [{
                            "account_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "date": "2025-01-23",
                            "amount": 0,
                            "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "payee_name": "string",
                            "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                            "memo": "string",
                            "cleared": "cleared",
                            "approved": true,
                            "flag_color": "red",
                            "subtransactions": [{
                                "amount": 0,
                                "payee_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "payee_name": "string",
                                "category_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "memo": "string"
                            }],
                            "import_id": "string"
                        }]
                    }
                }
                Use: Creates one or multiple transactions in the user's budget. Required fields are account_id, date, and amount. Amount must be in milliunits (e.g. $10.00 = 10000).
                """
            }
        },
        {
            "uuid": UUID("b4cc290f-9c8a-4d87-8c2c-5de21b52df73"),
            "name": "todoist",
            "description": "responsible for managing tasks and projects in Todoist",
            "instructions": {
                "get_projects": """
                {
                    "params": {}
                }
                Use: Retrieves all projects from Todoist
                """,
                "add_tasks": """
                {
                    "tasks": [{
                        "title": "Task title",
                        "description": "Task description", 
                        "priority": 1-4,
                        "projectId": "project_uuid",
                        "stateId": "state_uuid",
                        "estimate": number,
                        "labels": ["label1", "label2"],
                        "dueString": "tomorrow at 3pm",
                        "dueLang": "en",
                        "dueDate": "YYYY-MM-DD",
                        "duration": 30,
                        "durationUnit": "minute"
                    }]
                }
                Use: Adds one or more todos. Only title is required, other fields are optional
                """,
                "search_tasks": """
                {
                    "project_id": "optional_project_id",
                    "label": "optional_label_name",
                    "section_id": "optional_section_id",
                    "ids": ["optional_task_id1", "optional_task_id2"]
                }
                
                Use: Lists tasks filtered by any combination of:
                - project_id: Show tasks from a specific project
                - label: Show tasks with a specific label
                - section_id: Show tasks from a specific section
                - ids: Show specific tasks by their IDs
                Returns formatted list with task details including ids, title, priority, due dates, labels etc.
                """,
                "update_tasks": """
                {
                    "tasks": [{
                        "id": "task_id",
                        "content": "Updated task title",
                        "description": "Updated description",
                        "priority": 1-4,
                        "labels": ["label1", "label2"],
                        "dueString": "tomorrow at 3pm",
                        "dueLang": "en",
                        "dueDate": "YYYY-MM-DD",
                        "duration": 30,
                        "durationUnit": "minute"
                    }]
                }
                Use: Updates existing tasks. Task ID is required, other fields are optional and will only be updated if provided. 
                Don't use it to complete tasks, use the complete_tasks action instead.
                """,
                "complete_tasks": """
                {
                    "task_ids": ["task_id1", "task_id2"]
                }
                Use: Marks one or more tasks as complete. Requires task IDs.
                """
            }
        }
    ]

def get_tool_by_name(name)->Dict[str, Any]:
    tools = get_tools()
    for tool in tools:
        if tool['name'] == name:
            return tool
    return {}

def get_tools_by_names(names: List[str]) -> List[Dict[str, Any]]:
    """Get multiple tools by their names
    
    Args:
        names: List of tool names to fetch
        
    Returns:
        List of matching tool dictionaries
    """
    tools = []
    for name in names:
        tool = get_tool_by_name(name)
        if tool:
            tools.append(tool)
    return tools


def get_tool_action_instructions(tool_name: str, action_name: str) -> str:
    """Get the instructions for a specific tool action

    Args:
        tool_name: Name of the tool
        action_name: Name of the action

    Returns:
        str: Instructions for the specified tool action, or empty string if not found
    """
    tool = get_tool_by_name(tool_name)
    if not tool or 'instructions' not in tool:
        return ""
        
    instructions = tool['instructions'].get(action_name)
    if not instructions:
        return ""
        
    return instructions


tool_handlers = {
    "ynab": execute_ynab,
    "todoist": execute_todoist
}
