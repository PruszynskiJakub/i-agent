from typing import List

from modules.types import Tool


def parse_markdown_backticks(str) -> str:
    if "```" not in str:
        return str.strip()
    # Remove opening backticks and language identifier
    str = str.split("```", 1)[-1].split("\n", 1)[-1]
    # Remove closing backticks
    str = str.rsplit("```", 1)[0]
    # Remove any leading or trailing whitespace
    return str.strip()

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
