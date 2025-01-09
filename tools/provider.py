from typing import Any, Dict
from uuid import UUID

from ynab.service import execute_ynab


def get_tools():
    return [
        {
            "uuid": UUID("a3bb189e-8bf9-4c8b-9beb-5de10a41cf62"),
            "name": "ynab",
            "description": "responsible for managing budget, transactions etc",
            "instructions": """Use the following actions based on the user's request type:
            1. ADD TRANSACTION
            {
                "action": "add_transaction",
                "params": {
                    "user_query": "an exact query from the user"
                }
            }
            Use: Creates one or multiple transactions in the user's budget
            
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
    "ynab" : execute_ynab
}
