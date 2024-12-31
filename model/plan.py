from dataclasses import dataclass


@dataclass
class Plan:
    _thinking: str  # Explain why this specific step is the best next action, referencing key findings or context
    step: str  # Description of the single next step
    tool: str  # Exact name of the tool to use from the available tools
    tool_uuid: str  # UUID of the tool to use from the available tools
