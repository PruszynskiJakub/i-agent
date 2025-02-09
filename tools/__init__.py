from typing import Any, Dict, List
from uuid import UUID

from tools.todoist.service import execute_todoist
from tools.ynab.service import execute_ynab
from tools.resend.service import execute_resend
from tools.document_processor.service import execute_document_processor


def get_tools():
    return [
        {
            "uuid": UUID("d6ee492f-8d9a-4e88-9beb-6de21c52ef85"),
            "name": "document_processor",
            "description": "responsible for processing documents in various ways such as summarization, extraction, etc.",
            "actions": {
                "summarize": {
                    "description": "Summarizes one or more documents and creates a new document from their contents",
                    "instructions": """
                    {
                        "document_uuids": ["list of document UUIDs to process"]
                    }
                    
                    Field details:
                    - document_uuids: Required, list of document UUIDs to process
                    
                    Example:
                    {
                        "document_uuids": ["550e8400-e29b-41d4-a716-446655440000"]
                    }
                    """
                }
            }
        },
        {
            "uuid": UUID("c5dd391f-7d8a-4e99-8f3b-6de21c52ef84"),
            "name": "resend",
            "description": "responsible for sending emails via Resend service",
            "actions": {
                "send_email": {
                    "description": "Composes and sends an email based on natural language description with optional attachments. The recipient and sender are determined by the Resend service configuration.",
                    "instructions": """
                    {
                        "query": "Natural language description of the email to send",
                        "documents": ["optional list of document UUIDs to use as source material"]
                    }
                    
                    Field details:
                    - query: Required. Natural language description of what email to send. Should include:
                      * Subject/topic of the email
                      * Main content/message to convey
                      * Any specific formatting requirements
                      * The system will compose appropriate subject line and HTML content
                    - documents: Optional list of document UUIDs to use as source material.
                      Referenced documents will be used to generate the email content.
                    
                    Example:
                    {
                        "query": "Send a meeting summary email about yesterday's project review. Include the main discussion points about timeline changes and new feature requests.",
                        "documents": ["550e8400-e29b-41d4-a716-446655440000"] # Document containing meeting notes to summarize
                    }
                    
                    """
                }
            }
        },
        {
            "uuid": UUID("a3bb189e-8bf9-4c8b-9beb-5de10a41cf62"),
            "name": "ynab",
            "description": "responsible for managing budget, transactions etc., available only on direct request",
            "actions": {
                "add_transactions": {
                    "description": "Creates one or multiple transactions in the user's budget based on natural language description. Can handle single transactions or split transactions with multiple parts.",
                    "instructions": """
                    {
                        "query": "string describing the transaction"
                    }
                    
                    The query should contain transaction details like:
                    - Amount (required)
                    - Payee (optional)
                    - Account (optional)
                    - Category (optional)
                    - Date (optional)
                    - Split details (optional)
                    
                    Examples:
                    - "spent $50 at walmart yesterday"
                    - "transfer $1000 from checking to savings"
                    - "split $120 restaurant bill: $100 dining out, $20 tip"
                    """
                },
                "update_transaction": {
                    "description": "Updates an existing transaction's details. Only transaction ID is required, other fields are optional and will only be updated if provided.",
                    "instructions": """
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
                    
                    Field details:
                    - amount: Use negative for spending, positive for income
                    - cleared: Can be "cleared", "uncleared", or "reconciled"
                    - approved: Set to true to approve the transaction
                    
                    Example:
                    {
                        "id": "abc-123",
                        "amount": -5000,
                        "memo": "Monthly subscription",
                        "cleared": "cleared"
                    }
                    """
                }
            }
        },
        {
            "uuid": UUID("b4cc290f-9c8a-4d87-8c2c-5de21b52df73"),
            "name": "todoist",
            "description": "responsible for managing tasks and projects in Todoist",
            "actions": {
                "add_tasks": {
                    "description": "Creates one or more tasks in Todoist. Supports natural language for dates and rich task metadata.",
                    "instructions": """
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
                    
                    Field details:
                    - title: Required, task name
                    - priority: 4 (highest) to 1 (lowest)
                    - dueString: Natural language date ("tomorrow", "next monday 2pm")
                    - duration: Task duration number
                    - durationUnit: "minute", "hour", "day"
                    
                    Examples:
                    - Simple task: {"title": "Buy groceries"}
                    - Complex task: {
                        "title": "Quarterly review",
                        "priority": 4,
                        "dueString": "next friday 2pm",
                        "duration": 60,
                        "durationUnit": "minute"
                      }
                    """
                },
                "search_tasks": {
                    "description": "Searches and retrieves tasks using advanced filters, supporting complex queries with logical operators and field-based filtering",
                    "instructions": """
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
                     (e.g. "invoice" ↔ "faktura/faktury/faktur/invoice/invoices/invoicing"), 
                     the LLM should expand the terms to increase the likelihood of matches.
                   - Example:
                       "search: invoice | search: faktura | search: faktury search: faktur)"
                     This ensures tasks referencing any of those variations are included.
                
                4) Fuzzy Matching or Partial Matching (optional enhancement):
                   - You might integrate partial matches or wildcard expansions 
                     (e.g., "factur" to capture “facture,” “factur,” “factury,” etc.).
                   - Implement as relevant to your system’s capabilities.
                
                5) Multi-Condition Combining:
                   - Combine synonyms with other logical filters.
                   - Example:
                       "(search: invoice | search: faktura | search: faktury) & !status: done"
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
                For a user request: “Mark as complete a task labeled pc related to invoice - faktury in project Inbox”
                the system might expand synonyms and produce a filter:
                  {
                    "filter": "(search: invoice | search: faktura | search: faktury | search: faktur) & !status: done",
                    "project_id": "2334150459",
                    "label": "pc"
                  }
                This ensures capturing multiple linguistic variations of "invoice."
             
                Returns formatted list with task details including ids, title, priority, due dates, labels etc.
                """
                },
                "update_tasks": {
                    "description": "Updates existing tasks with new content, metadata, or settings while preserving task history and relationships",
                    "instructions": """
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
                """
                },
                "complete_tasks": {
                    "description": "Marks one or more tasks as complete, updating their status and completion timestamp",
                    "instructions": """
                {
                    "task_ids": ["task_id1", "task_id2"]
                }
                Use: Marks one or more tasks as complete. Requires task IDs.
                """
                },
                "move_tasks": {
                    "description": "Reorganizes tasks by moving them between projects, sections, or parent tasks while maintaining their metadata",
                    "instructions": """
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
    if not tool or 'actions' not in tool:
        return ""
        
    action = tool['actions'].get(action_name)
    if not action:
        return ""
        
    if isinstance(action, dict):
        return action.get('instructions', "")
    
    # Handle legacy format where action is just instructions string
    return action


tool_handlers = {
    "ynab": execute_ynab,
    "todoist": execute_todoist,
    "resend": execute_resend,
    "document_processor": execute_document_processor
}
