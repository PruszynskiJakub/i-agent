from typing import List, Dict
from openai import OpenAI

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def completion(self, model: str, messages: List[Dict[str, str]]) -> str:
        """
        Get completion from OpenAI API
        
        Args:
            model: OpenAI model to use (e.g. "gpt-3.5-turbo")
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            Model response as string
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
