from typing import Any, Dict, List
from uuid import UUID

from tools.document_processor.service import execute_document_processor
from tools.make.service import execute_make
from tools.resend.service import execute_resend
from tools.todoist.service import execute_todoist
from tools.web.service import execute_web
from tools.ynab.service import execute_ynab


def get_tools():
    tools = [
        {
            "uuid": UUID("f8dd593f-8c9b-4e88-9beb-8de21c52ef74"),
            "name": "make",
            "description": "responsible for creating invoices and automating workflows",
            "actions": {
                "invoice": {
                    "description": "Creates a new invoice based on the number of days worked in the current month and uploads it to Google Drive",
                    "instructions": """
                    {
                        "days_worked": "Number of days worked in the current month (required)"
                    }
                    
                    Field details:
                    - days_worked: Required. Integer representing the number of days worked in the current month.
                    
                    Example:
                    {
                        "days_worked": 15
                    }
                    
                    Returns:
                    Information about the created invoice including confirmation of upload to Google Drive.
                    """
                }
            }
        },
        {
            "uuid": UUID("0852748f-6211-41bb-bcfa-d81716fe84e7"),
            "name": "final_answer",
            "description": "responsible for providing the final answer to the user's query",
            "actions": {
                "respond": {
                    "description": "Responds to the user with the final answer to their query",
                    "instructions": """
                        {
                            "answer": "Final answer to the user query"
                        }
                        """
                }
            }
        },
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
                        "documents": ["list of document UUIDs to use as source material"]
                    }
                    
                    Field details:
                    - query: Required. Natural language description of what email to send. Should include:
                      * Subject/topic of the email
                      * Main content/message to convey
                      * Any specific formatting requirements
                      * The system will compose appropriate subject line and HTML content
                    - documents: Required list of document UUIDs to use as source material.
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
                    "description": "Creates one or more todo items in Todoist. Supports natural language for dates and rich task metadata.",
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
                    "description": "Searches and retrieves todo items using basic filters for dates, projects, and labels",
                    "instructions": """
                    {
                      "project_id": "Optional project ID to narrow down tasks",
                      "ids": ["Optional list of specific task IDs"],
                      "due_before": "Optional date in YYYY-MM-DD format",
                      "due_after": "Optional date in YYYY-MM-DD format"
                    }
                    
                    Field details:
                    - project_id: Exact project ID to filter tasks
                    - ids: List of specific task IDs to retrieve
                    - due_before: Include tasks due before this date (inclusive)
                    - due_after: Include tasks due after this date (inclusive)
                    
                    Example:
                    {
                      "project_id": "2334150459",
                      "due_before": "2024-12-31",
                      "due_after": "2024-01-01"
                    }
                    
                    Returns:
                    A list of matching todo items with their IDs, titles, due dates,
                    projects and labels.
                """
                },
                "update_tasks": {
                    "description": "Updates existing todo items with new content, metadata, or settings while preserving item history and relationships",
                    "instructions": """
                    {
                        "items": [{
                            "id": "todo_item_id",
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
                    
                    Usage:
                    - Updates existing tasks' content and metadata
                    - Todo item ID is required, other fields are optional
                    - Do not use for completing tasks (use complete_tasks instead)
                    - Do not use for moving tasks (use move_tasks instead)
                    """
                },
                "complete_tasks": {
                    "description": "Marks one or more todo items as completed, updating their status and completion timestamp",
                    "instructions": """
                    {
                        "ids": ["id1", "id2"]
                    }
                    
                    Usage:
                    - Marks one or more todo items as complete
                    - Requires items IDs
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
                    
                    Usage:
                    - Moves tasks between projects, sections, or parent tasks
                    - Task ID is required
                    - Provide exactly one destination: project_id, section_id, or parent_id
                    """
                }
            }
        },
        {
            "uuid": UUID("e7ff593f-9d9b-4f99-8c3c-7de32c63df96"),
            "name": "web",
            "description": "responsible for web search, web scraping and content extraction",
            "actions": {
                "search": {
                    "description": """Performs targeted web searches across trusted domains including Wikipedia, OpenAI, and Anthropic. Uses advanced query enhancement to find the most relevant results.""",
                    "instructions": """
                        {
                            "query": "Search query string describing what information to find"
                        }

                        Field details:
                        - query: Required. Natural language description of what to search for. The system will:
                          * Enhance the query with domain-specific terms
                          * Add appropriate search operators
                          * Target trusted domains like:
                            - wikipedia.org (encyclopedic knowledge)
                            - openai.com (AI technology and news)
                            - anthropic.com (AI research and updates)

                        Examples:
                        {
                            "query": "Latest developments in large language models"
                        }
                        Will search AI company domains for recent LLM advances

                        {
                            "query": "Explain how neural networks work"
                        }
                        Will search Wikipedia and educational sources for explanatory content

                        {
                            "query": "GPT-4 capabilities and limitations"
                        }
                        Will search OpenAI's documentation and announcements

                        Returns structured results containing:
                        - Page titles
                        - Relevant text snippets
                        - Source URLs
                        - Domain information
                        """
                },
                # "scrape": {
                #     "description": "Scrapes content from a web page. USE ONLY if URL is given or known in any other case use search action to obtain URL",
                #     "instructions": """
                #     {
                #         "url": "URL to scrape"
                #     }
                #
                #     Field details:
                #     - url: Required. The web page URL to scrape
                #
                #     Example:
                #     {
                #         "url": "https://example.com/article"
                #     }
                #
                #     USE ONLY if URL is given or known
                #     """
                # }
            }
        }
    ]
    
    for tool in tools:
        if "actions" in tool:
            actions = tool.pop("actions")
            bullet_points = []
            for action_name, action_data in actions.items():
                # Remove extra whitespace from the instructions string
                instr = action_data.get("instructions", "").strip()
                bullet_points.append(f"- Tool action:  {action_name}: {instr}")
            tool["instructions"] = "\n".join(bullet_points)
            
    return tools


def get_tool_by_name(name) -> Dict[str, Any]:
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
    "document_processor": execute_document_processor,
    "web": execute_web,
    "make": execute_make
}
