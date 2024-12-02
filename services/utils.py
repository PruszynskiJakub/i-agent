def parse_markdown_backticks(str) -> str:
    if "```" not in str:
        return str.strip()
    # Remove opening backticks and language identifier
    str = str.split("```", 1)[-1].split("\n", 1)[-1]
    # Remove closing backticks
    str = str.rsplit("```", 1)[0]
    # Remove any leading or trailing whitespace
    return str.strip()

def format_tools_for_prompt(tools_mapping: dict) -> str:
    """Formats the available tools into a string for the prompt
    
    Args:
        tools_mapping: Dictionary mapping tool names to tool objects
        
    Returns:
        str: Formatted string describing all available tools
    """
    tool_descriptions = []
    for tool in tools_mapping.values():
        desc = f"Tool: {tool.name}\n"
        desc += f"Description: {tool.description}\n"
        desc += "Required parameters:\n"
        for param, param_desc in tool.required_params.items():
            desc += f"- {param}: {param_desc}\n"
        if hasattr(tool, 'optional_params'):
            desc += "Optional parameters:\n"
            for param, param_desc in tool.optional_params.items():
                desc += f"- {param}: {param_desc}\n"
        tool_descriptions.append(desc)
    return "\n".join(tool_descriptions)