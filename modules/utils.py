from typing import List

from modules.types import Tool, Action


def parse_markdown_backticks(str) -> str:
    if "```" not in str:
        return str.strip()
    # Remove opening backticks and language identifier
    str = str.split("```", 1)[-1].split("\n", 1)[-1]
    # Remove closing backticks
    str = str.rsplit("```", 1)[0]
    # Remove any leading or trailing whitespace
    return str.strip()

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
        
        # Add result information if it's a Document
        if hasattr(action.result, 'metadata'):
            desc += "  <result>\n"
            desc += f"    <source>{action.result['metadata'].get('source', '')}</source>\n"
            desc += "  </result>\n"
        
        desc += "</action>"
        action_descriptions.append(desc)
    return "\n".join(action_descriptions)

def format_tools_for_prompt(tools_mapping: List[Tool]) -> str:
    """Formats the available tools into a string for the prompt
    
    Args:
        tools_mapping: List of Tool objects
        
    Returns:
        str: Formatted string describing all available tools
    """
    tool_descriptions = []
    for tool in tools_mapping:
        desc = f"<tool name='{tool.name}' description='{tool.description}'>\n"
        if tool.required_params:
            desc += "  <required_params>\n"
            for param, param_desc in tool.required_params.items():
                desc += f"    <param name='{param}'>{param_desc}</param>\n"
            desc += "  </required_params>\n"
        if tool.optional_params:
            desc += "  <optional_params>\n"
            for param, param_desc in tool.optional_params.items():
                desc += f"    <param name='{param}'>{param_desc}</param>\n"
            desc += "  </optional_params>\n"
        desc += "</tool>"
        tool_descriptions.append(desc)
    return "\n".join(tool_descriptions)
