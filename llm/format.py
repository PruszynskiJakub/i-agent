from ast import Dict
from typing import List
from datetime import datetime

from models.action import ActionRecord
from models.document import Document
from models.message import Message
from models.state import ToolThought


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


def format_messages(messages: List[Message]) -> List[dict]:
    """
    Formats messages for completion by ensuring each message is a dictionary
    with 'role' and 'content' keys.

    Args:
        messages: List of message dictionaries

    Returns:
        List of formatted message dictionaries
    """
    formatted_messages = []
    for message in messages:
        formatted_message = {
            "role": message.role,
            "content": message.content
        }
        formatted_messages.append(formatted_message)
    return formatted_messages


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


def format_tools_with_instructions(tools: List[Dict]) -> str:
    """
    Formats a list of tools into an XML-like string representation.

    Args:
        tools: List of tool dictionaries

    Returns:
        str: Formatted string describing all tools with their action instructions
    """
    tool_descriptions = []
    for tool in tools:
        desc = f"<tool uuid='{tool['uuid']}'>\n"
        desc += f"  <name>{tool['name']}</name>\n"
        desc += f"  <description>{tool['description']}</description>\n"
        desc += "  <actions>\n"
        if 'actions' in tool:
            for action_name, action_info in tool['actions'].items():
                desc += f"    <action name='{action_name}'>\n"
                if isinstance(action_info, dict):
                    desc += f"      <description>{action_info['description']}</description>\n"
                    desc += f"      <instructions>{action_info['instructions']}</instructions>\n"
                else:
                    # Handle legacy format where action_info is just instructions string
                    desc += f"      <instructions>{action_info}</instructions>\n"
                desc += "    </action>\n"
        desc += "  </actions>\n"
        desc += "</tool>"
        tool_descriptions.append(desc)
    return "\n".join(tool_descriptions)

def format_tool_instructions(tool) -> str:
    desc = f"  <name>{tool['name']}</name>\n"
    desc += f"  <description>{tool['description']}</description>\n"
    desc += "  <actions>\n"
    if 'actions' in tool:
        for action_name, action_info in tool['actions'].items():
            desc += f"    <action name='{action_name}'>\n"
            if isinstance(action_info, dict):
                desc += f"      <description>{action_info['description']}</description>\n"
                desc += f"      <instructions>{action_info['instructions']}</instructions>\n"
            else:
                # Handle legacy format where action_info is just instructions string
                desc += f"      <instructions>{action_info}</instructions>\n"
            desc += "    </action>\n"
    desc += "  </actions>\n"
    return desc


def format_tool_candidates(tool_candidates: List[ToolThought]) -> str:
    """
    Formats tool candidates into an XML-like string representation.

    Args:
        tool_candidates: List of ToolCandidate objects

    Returns:
        str: Formatted string describing all tool candidates
    """
    candidate_descriptions = []
    for candidate in tool_candidates:
        desc = "<tool_candidate>\n"
        desc += f"  <tool>{candidate.tool_name}</tool>\n"
        desc += f"  <reason>{candidate.reason}</reason>\n"
        desc += f"  <query>{candidate.query}</query>\n"
        desc += "</tool_candidate>"
        candidate_descriptions.append(desc)
    return "\n".join(candidate_descriptions)


def format_interaction(interaction) -> str:
    """
    Formats an Interaction object into an XML-like string representation.

    Args:
        interaction: Interaction object to format

    Returns:
        str: Formatted string describing the interaction
    """
    desc = "<interaction>\n"
    desc += f"  <overview>{interaction.overview}</overview>\n"
    desc += f"  <tool>{interaction.tool}</tool>\n"
    if interaction.tool_uuid:
        desc += f"  <tool_uuid>{interaction.tool_uuid}</tool_uuid>\n"
    desc += f"  <tool_action>{interaction.tool_action}</tool_action>\n"
    desc += f"  <query>{interaction.query}</query>\n"
    desc += "</interaction>"
    return desc


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


def format_tools_with_descriptions(tools: List[Dict]) -> str:
    """
    Formats a list of tools into an XML-like string representation including action descriptions.

    Args:
        tools: List of tool dictionaries

    Returns:
        str: Formatted string describing all tools with their action descriptions
    """
    tool_descriptions = []
    for tool in tools:
        desc = f"<tool uuid='{tool['uuid']}'>\n"
        desc += f"  <name>{tool['name']}</name>\n"
        desc += f"  <description>{tool['description']}</description>\n"
        desc += "  <actions>\n"
        if 'actions' in tool:
            for action_name, action_info in tool['actions'].items():
                desc += f"    <action name='{action_name}'>\n"
                if isinstance(action_info, dict):
                    desc += f"      <description>{action_info['description']}</description>\n"
                else:
                    # Handle legacy format where action_info is just instructions string
                    desc += f"      <description>Action instructions available</description>\n"
                desc += "    </action>\n"
        desc += "  </actions>\n"
        desc += "</tool>"
        tool_descriptions.append(desc)
    return "\n".join(tool_descriptions)


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
    """
