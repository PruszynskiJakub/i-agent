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
                    "query": "string describing the transaction"
                }
                Use: Creates one or multiple transactions in the user's budget based on the natural language description in the query field.
                The query should contain all necessary transaction details like amount, payee, account, etc. or at least amount.
                
                """,
                "update_transaction": """
                {
                    "id": "transaction_id",
                    "account_id": "optional account uuid",
                    "date": "optional YYYY-MM-DD",
                    "amount": "optional integer in milliunits (e.g. -10025 for -$10.025 spending, 10025 for $10.025 income)",
                    "payee_id": "optional payee uuid",
                    "category_id": "optional category uuid",
                    "memo": "optional string",
                    "cleared": "optional cleared status",
                    "approved": "optional boolean"
                }
                Use: Updates an existing transaction. Only transaction id is required, other fields are optional and will only be updated if provided.
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
                  "filter": "Optional advanced query string with logical operators, field filters, and synonym expansions",
                  "project_id": "Optional project ID to narrow down tasks",
                  "label": "Optional label name to narrow down tasks",
                  "section_id": "Optional section ID to narrow down tasks",
                  "ids": ["Optional list of exact task IDs"]
                }
                
                
                Usage:
                Fetch based on an advanced search.  
                The "filter" field can include:
                
                1) Logical Operators:
                   - & (AND), | (OR), ! (NOT)
                   - Parentheses for grouping (e.g., "(p1 | p2) & overdue")
                
                2) Field-based Filters:
                   - Examples: "title:", "assigned to:", "created:", "status:", "due:", etc.
                   - "search:" for free-text searches over task content/title.
                
                3) Synonym and Morphological Expansion:
                   - When the user query suggests synonyms or variant forms 
                     (e.g. "invoice" ↔ "faktura/faktury/faktur"), 
                     the LLM should expand the terms to increase the likelihood of matches.
                   - Example:
                       "search: (invoice OR faktura OR faktury OR faktur)"
                     This ensures tasks referencing any of those variations are included.
                
                4) Fuzzy Matching or Partial Matching (optional enhancement):
                   - You might integrate partial matches or wildcard expansions 
                     (e.g., "factur" to capture “facture,” “factur,” “factury,” etc.).
                   - Implement as relevant to your system’s capabilities.
                
                5) Multi-Condition Combining:
                   - Combine synonyms with other logical filters.
                   - Example:
                       "search: (invoice OR faktura OR faktury) & !status: done"
                     This finds tasks mentioning “invoice” or “faktura/faktury,” excluding completed ones.
                
                6) Additional Filtering Fields:
                   - "project_id": Restrict results to a specific project by its ID.
                   - "label": Filter by a specific label (like “urgent”).
                   - "section_id": Filter tasks in a specific project section.
                   - "ids": Retrieve a specific list of tasks by their unique IDs.
                
                Returns:
                - A structured JSON list containing relevant task details 
                  (task IDs, title, priority, due dates, labels, assignments, etc.).
                
                Example:
                For a user request: “Mark as complete a task related to invoice - faktury”
                the system might expand synonyms and produce a filter:
                  {
                    "filter": "search: (invoice OR faktura OR faktury OR faktur) & !status: done"
                  }
                This ensures capturing multiple linguistic variations of "invoice."
             
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
                Use: Updates existing tasks' content and metadata. Task ID is required, other fields are optional and will only be updated if provided.
                Don't use it to complete tasks (use complete_tasks) or move tasks between projects/sections (use move_tasks).
                """,
                "complete_tasks": """
                {
                    "task_ids": ["task_id1", "task_id2"]
                }
                Use: Marks one or more tasks as complete. Requires task IDs.
                """,
                "move_tasks": """
                {
                    "tasks": [{
                        "id": "task_id",
                        "project_id": "optional target project id",
                        "section_id": "optional target section id", 
                        "parent_id": "optional parent task id"
                    }]
                }
                Use: Moves tasks between projects, sections, or changes their parent task. Task ID is required, provide at least one destination (project_id, section_id, or parent_id).
                Only one destination type should be specified per task move operation.
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
