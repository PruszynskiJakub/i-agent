from ast import Dict
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Plan:
    _thinking: str  # Explain why this specific step is the best next action, referencing key findings or context
    step: str  # Description of the single next step
    tool: str  # Exact name of the tool to use from the available tools
    tool_uuid: str

@dataclass(frozen=True)
class Definition:
    _thinking: str  # Explain why this specific step is the best next action, referencing key findings or context
    tool: str  # The tool to use
    step: str  # The step to take with the tool
    action: str  # The action to take with the tool
    params: dict[str, Any]  # The parameters for the action
    