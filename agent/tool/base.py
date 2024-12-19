from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List
from uuid import UUID

from model.action import ActionResult
from model.document import Document

@dataclass
class Tool(ABC):
    """A tool that can be used by the agent"""
    uuid: UUID
    name: str
    description: str
    instructions: str
    required_params: Dict[str, str]
    optional_params: Dict[str, str]

    @abstractmethod
    async def execute(self, params: Dict[str, Any], docs: List[Document], trace: Any) -> ActionResult:
        """Execute the tool with the given parameters and documents
        
        Args:
            params: Dictionary of parameters for the tool execution
            docs: List of documents to process
            trace: Trace object for logging/debugging purposes
            
        Returns:
            Tool execution result
        """
        pass
