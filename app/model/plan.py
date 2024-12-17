from dataclasses import dataclass


@dataclass
class Plan:
    _thinking: str  # Explain why this specific step is the best next action, referencing key findings or context
    step: str  # Description of the single next step
    tool: str  # Exact name of the tool to use from the available tools
    parameters: dict  # Parameters for the tool, e.g., {"param1": "value1", "param2": "value2"}
    required_information: list  # List of specific information we need to extract from this step's result
