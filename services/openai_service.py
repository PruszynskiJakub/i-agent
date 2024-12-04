from typing import List, Dict
from openai import AsyncOpenAI
from langsmith import traceable

@traceable

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = traceable(AsyncOpenAI)(api_key=api_key)
    
    async def completion(self, messages: List[Dict[str, str]], model: str = "gpt-4o-mini", json_mode: bool = False) -> str:
        """
        Get completion from OpenAI API
        
        Args:
            model: OpenAI model to use (e.g. "gpt-3.5-turbo")
            messages: List of message dictionaries with 'role' and 'content' keys
            json_mode: If True, sets response_format to JSON (default: False)
            
        Returns:
            Model response as string
        """
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"} if json_mode else {"type": "text"}
        )
        return response.choices[0].message.content
