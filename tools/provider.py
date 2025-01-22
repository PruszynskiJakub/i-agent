from typing import Any, Dict
from uuid import UUID

from todoist.service import execute_todoist
from ynab.service import execute_ynab


def get_tools():
    return [
        {
            "uuid": UUID("a3bb189e-8bf9-4c8b-9beb-5de10a41cf62"),
            "name": "ynab",
            "description": "responsible for managing budget, transactions etc., available only on direct request",
            "instructions": """Use the following actions based on the user's request type:
            1. ADD TRANSACTION
            {
                "action": "add_transaction",
                "params": {
                    "query": "The query representing a full transaction or list of transactions 
                    including amount, accounts, currencies and key details required to categorize it properly"
                }
            }
            Use: Creates one or multiple transactions in the user's budget
            
            """
        },
        {
            "uuid": UUID("b4cc290f-9c8a-4d87-8c2c-5de21b52df73"),
            "name": "todoist",
            "description": "responsible for managing tasks and projects in Todoist",
            "instructions": """Use the following actions based on the user's request type:
            1. GET PROJECTS
            {
                "action": "get_projects",
                "params": {}
            }
            Use: Retrieves all projects from Todoist

            2. ADD TASKS
            {
                "action": "add_tasks",
                "params": {
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
            }
            Use: Adds one or more todos. Only title is required, other fields are optional

            3. SEARCH TASKS
            {
                "action": "search_tasks",
                "params": {
                    "project_id": "optional_project_id",
                    "label": "optional_label_name",
                    "section_id": "optional_section_id",
                    "ids": ["optional_task_id1", "optional_task_id2"]
                }
            }
            Use: Lists tasks filtered by any combination of:
            - project_id: Show tasks from a specific project
            - label: Show tasks with a specific label
            - section_id: Show tasks from a specific section
            - ids: Show specific tasks by their IDs
            Returns formatted list with task details including ids, title, priority, due dates, labels etc.

            4. UPDATE TASKS
            {
                "action": "update_tasks",
                "params": {
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
            }
            Use: Updates existing tasks. Task ID is required, other fields are optional and will only be updated if provided. 
            Don't use it to complete tasks, use the complete_tasks action instead.

            5. COMPLETE TASKS
            {
                "action": "complete_tasks", 
                "params": {
                    "task_ids": ["task_id1", "task_id2"]
                }
            }
            Use: Marks one or more tasks as complete. Requires task IDs.
            """
        }
    ]

def get_tool_by_name(name)->Dict[str, Any]:
    tools = get_tools()
    for tool in tools:
        if tool['name'] == name:
            return tool
    return {}


tool_handlers = {
    "ynab": execute_ynab,
    "todoist": execute_todoist
}
