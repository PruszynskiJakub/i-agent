from typing import List, Dict
from services.openai_service import OpenAIService
from services.logging_service import LoggingService

class Agent:
    def __init__(self, service: OpenAIService):
        self.service = service
        self.logger = LoggingService()
        
    async def run(self, message: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Run the agent with an initial message
        
        Args:
            message: Initial message to send
            model: OpenAI model to use (default: gpt-3.5-turbo)
            
        Returns:
            Model response as string
        """
        self.logger.log_input(message)
        
        messages = [
            {"role": "user", "content": message}
        ]
        
        response = await self.service.completion(
            model=model,
            messages=messages
        )
        
        self.logger.log_output(response)
        return response
