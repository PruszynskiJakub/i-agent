from ast import Dict
from typing import List

from tools.types import Action
from agent.types import Message


def format_actions(actions: List[Action]) -> str:
    """Formats the executed actions into a string for the prompt

    Args:
        actions: List of Action objects

    Returns:
        str: Formatted string describing all executed actions
    """
    action_descriptions = []
    for action in actions:
        desc = f"<action name='{action.name}' step='{action.step_description}'>\n"
        desc += "  <parameters>\n"
        for param_name, param_value in action.payload.items():
            desc += f"    <param name='{param_name}'>{param_value}</param>\n"
        desc += "  </parameters>\n"

        # Add result information
        desc += "  <result>\n"
        desc += f"    {action.result}"
        if action.documents:
            desc += "    <documents>\n"
            for doc in action.documents:
                desc += f"      <document source='{doc['metadata'].get('source', '')}'>\n"
                desc += f"        <description>{doc['metadata'].get('description', '')}</description>\n"
                desc += "      </document>\n"
            desc += "    </documents>\n"
        desc += "  </result>\n"
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

def format_tool_instructions(tool) -> str:
    desc = f"  <name>{tool['name']}</name>\n"
    desc += f"  <description>{tool['description']}</description>\n"
    desc += f"  <instructions>{tool['instructions']}</instructions>\n"
    return desc

def format_document(document) -> str:
    """
    Formats a document's metadata into an XML-like string representation,
    excluding the document text content.

    Args:
        document: Document object

    Returns:
        str: Formatted string describing the document metadata
    """
    desc = f"<document uuid='{document.uuid}'>\n"
    desc += f"  <conversation>{document.conversation_uuid}</conversation>\n"
    
    # Add metadata if present
    if document.metadata:
        desc += "  <metadata>\n"
        for key, value in document.metadata.items():
            if isinstance(value, list):
                desc += f"    <{key}>\n"
                for item in value:
                    desc += f"      <item>{item}</item>\n"
                desc += f"    </{key}>\n"
            else:
                desc += f"    <{key}>{value}</{key}>\n"
        desc += "  </metadata>\n"
    
    desc += "</document>"
    return desc
