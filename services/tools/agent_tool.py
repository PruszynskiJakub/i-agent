from abc import ABC, abstractmethod

class AgentTool(ABC):
    """Base class for all agent tools"""

    name = "base_tool"
    description = "Base tool description"
    required_params = {}
    optional_params = {}

    @abstractmethod
    def execute(self, params: dict) -> any:
        """Execute the tool with given parameters"""
        pass