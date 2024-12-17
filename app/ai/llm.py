from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from openai import AsyncOpenAI

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        """
        Get completion from LLM
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            model: Model identifier to use (provider-specific)
            json_mode: Whether to request JSON response
            
        Returns:
            Model response as string
        """
        pass

