from typing import List, Dict
from openai import OpenAI

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def completion(self, model: str, messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        """
        Get completion from OpenAI API
        
        Args:
            model: OpenAI model to use (e.g. "gpt-3.5-turbo")
            messages: List of message dictionaries with 'role' and 'content' keys
            json_mode: If True, sets response_format to JSON (default: False)
            
        Returns:
            Model response as string
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"} if json_mode else {"type": "text"}
        )
        return response.choices[0].message.content
