from typing import List, Dict
from services.openai_service import OpenAIService

class Agent:
    def __init__(self, service: OpenAIService):
        self.service = service
        
    async def run(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Run the agent with an initial message
        
        Args:
            message: Initial message to send
            model: OpenAI model to use (default: gpt-3.5-turbo)
            
        Returns:
            Model response as string
        """
        messages = [
            {"role": "user", "content": message}
        ]
        
        return await self.service.completion(
            model=model,
            messages=messages
        )
