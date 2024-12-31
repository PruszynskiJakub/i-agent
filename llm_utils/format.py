from typing import List

from model.action import Action
from model.message import Message


def format_actions_for_prompt(actions: List[Action]) -> str:
    """Formats the executed actions into a string for the prompt

    Args:
        actions: List of Action objects

    Returns:
        str: Formatted string describing all executed actions
    """
    action_descriptions = []
    for action in actions:
        desc = f"<action name='{action.name}'>\n"
        desc += "  <parameters>\n"
        for param_name, param_value in action.payload.items():
            desc += f"    <param name='{param_name}'>{param_value}</param>\n"
        desc += "  </parameters>\n"

        # Add result information
        desc += "  <result>\n"
        desc += f"    <output>{action.result}</output>\n"
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


def format_messages_for_completion(messages: List[Message]) -> List[dict]:
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

