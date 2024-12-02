from abc import ABC, abstractmethod

class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the tool"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does"""
        pass
    
    @abstractmethod
    async def run(self, input_text: str) -> str:
        """Execute the tool's action"""
        pass
