from ast import Dict
from datetime import datetime
from typing import List

from models.document import Document
from agent.state import Task, Thoughts


def format_tools(tools: List[Dict]) -> str:
    """
    Formats a list of tools into an XML-like string representation.

    Args:
        tools: List of tool dictionaries

    Returns:
        str: Formatted string describing all tools
    """
    tool_descriptions = []
    for tool in tools:
        desc = f"<tool uuid='{tool['uuid']}'>\n"
        desc += f"  <name>{tool['name']}</name>\n"
        desc += f"  <description>{tool['description']}</description>\n"
        if tool.get("instructions", "").strip():
            desc += f"  <instructions>\n{tool.get('instructions').strip()}\n</instructions>\n"
        desc += "</tool>"
        tool_descriptions.append(desc)
    return "\n".join(tool_descriptions)


def format_documents(documents: List[Document]) -> str:
    """
    Formats multiple documents' metadata into an XML-like string representation with JSON metadata,
    excluding the document text content.

    Args:
        documents: List of Document objects

    Returns:
        str: Formatted string describing the documents' metadata
    """

    doc_descriptions = []
    for document in documents:
        desc = f"<document uuid='{document.uuid}'>\n"

        # Add metadata as individual XML tags
        if document.metadata:
            if 'name' in document.metadata:
                desc += f"  <name>{document.metadata['name']}</name>\n"
            if 'description' in document.metadata:
                desc += f"  <desc>{document.metadata['description']}</desc>\n"
            if 'mime_type' in document.metadata:
                desc += f"  <mime_type>{document.metadata['mime_type']}</mime_type>\n"

        # Add document text
        desc += f"  <text>{document.text}</text>\n"
        desc += "</document>"
        doc_descriptions.append(desc)

    return "\n".join(doc_descriptions)


def format_thoughts(thoughts: Thoughts) -> str:
    """
    Formats Thoughts into an XML-like string representation.

    Args:
        thoughts: Thoughts object containing user intent and tool thoughts

    Returns:
        str: Formatted string describing thoughts and tool candidates
    """
    result = "<thoughts>\n"
    result += f"  <user_intent>{thoughts.user_intent}</user_intent>\n"

    if thoughts.tool_thoughts:
        result += "  <tool_thoughts>\n"
        for thought in thoughts.tool_thoughts:
            result += "    <tool_thought>\n"
            result += f"      <query>{thought.query}</query>\n"
            result += f"      <tool>{thought.tool_name}</tool>\n"
            result += "    </tool_thought>\n"
        result += "  </tool_thoughts>\n"

    result += "</thoughts>"
    return result


def format_tasks(tasks: List[Task]) -> str:
    """
    Formats a list of tasks into an XML-like string representation.

    Args:
        tasks: List of Task objects

    Returns:
        str: Formatted string describing all tasks and their actions
    """
    task_descriptions = []
    for task in tasks:
        desc = f"<task uuid='{task.uuid}'>\n"
        desc += f"  <name>{task.name}</name>\n"
        desc += f"  <description>{task.description}</description>\n"
        desc += f"  <status>{task.status}</status>\n"

        if task.actions:
            desc += "  <actions>\n"
            for action in task.actions:
                desc += f"    <action uuid='{action.uuid}'>\n"
                desc += f"      <name>{action.name}</name>\n"
                desc += f"      <tool>{action.tool_uuid}</tool>\n"
                desc += f"      <step>{action.step}</step>\n"
                desc += f"      <status>{action.status}</status>\n"
                if action.output_documents:
                    desc += "      <documents>\n"
                    for doc in action.output_documents:
                        desc += f"        <document uuid='{doc.uuid}' type='{doc.metadata.get('type', 'unknown')}'>\n"
                        desc += f"          <text>{doc.text}</text>\n"
                        desc += "        </document>\n"
                    desc += "      </documents>\n"
                desc += "    </action>\n"
            desc += "  </actions>\n"

        desc += "</task>"
        task_descriptions.append(desc)

    return "\n".join(task_descriptions)


def format_facts() -> str:
    """
    Returns formatted facts about current date.

    Returns:
        str: Current date in YYYY-MM-DD format
    """
    today = datetime.now()
    return f"""
    - Current date - {today.strftime('%Y-%m-%d')}
    - Username is Kuba
    - Your name is iAgent
    """


def format_tool(tool: str) -> str:
    """
    Formats a single tool into an XML-like string representation including its name,
    tool actions, and their descriptions.

    Args:
        tool (str): The name of the tool to format.

    Returns:
        str: Formatted string with the tool name and its actions.
    """
    from tools import get_tool_by_name  # Import to lookup tool details

    tool_data = get_tool_by_name(tool)

    result = f"<tool uuid='{tool_data.get('uuid', 'unknown')}'>\n"
    result += f"  <name>{tool_data.get('name', tool)}</name>\n"
    result += f"  <description>{tool_data.get('description', '')}</description>\n"

    instructions = tool_data.get("instructions", "").strip()
    if instructions:
        result += f"  <instructions>{instructions}</instructions>\n"

    result += "</tool>"
    return result
