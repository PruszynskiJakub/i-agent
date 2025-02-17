from ast import Dict
from datetime import datetime
from typing import List

from models.action import ActionRecord
from models.document import Document
from models.state import Task, Thoughts


def format_actions_history(actions: List[ActionRecord]) -> str:
    """Formats the executed actions into a string for the prompt

    Args:
        actions: List of ActionRecord objects

    Returns:
        str: Formatted string describing all executed actions
    """
    action_descriptions = []
    for action in actions:
        desc = f"<action name='{action.name}' tool='{action.tool}'>\n"
        desc += "  <parameters>\n"
        for param_name, param_value in action.input_payload.items():
            desc += f"    <param name='{param_name}'>{param_value}</param>\n"
        desc += "  </parameters>\n"
        desc += f"  <status>{action.status}</status>\n"
        desc += f"  <description>{action.step_description}</description>\n"
        if action.output_documents:
            desc += "  <documents>\n"
            for doc in action.output_documents:
                desc += f"    <document uuid='{doc.uuid}' type='{doc.metadata['type']}'>\n"
                desc += f"      <text>{doc.text}</text>\n"
                desc += "    </document>\n"
            desc += "  </documents>\n"
        desc += "</action>"
        action_descriptions.append(desc)
    return "\n".join(action_descriptions)


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
