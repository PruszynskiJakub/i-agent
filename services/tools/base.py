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

    @property
    @abstractmethod
    def instructions(self) -> str:
        """Detailed instructions on how to use the tool"""
        pass
    
    @abstractmethod
    async def run(self, input_data: dict) -> dict:
        """Execute the tool's action"""
        pass
