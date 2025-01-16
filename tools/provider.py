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
