from typing import List, Dict
from services.openai_service import OpenAIService
from services.logging_service import LoggingService
from services.tools.final_answer import FinalAnswerTool

class Agent:
    def __init__(self, service: OpenAIService):
        self.service = service
        self.logger = LoggingService()
        self.tools = [FinalAnswerTool()]
        
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
        
        # Create system message with tools information
        tools_description = "\n".join([f"- {tool.name}: {tool.description}" for tool in self.tools])
        system_message = f"""You are a helpful AI assistant. You have access to the following tools:

{tools_description}

To use a tool, respond with:
TOOL: <tool_name>
INPUT: <input_text>

For your final answer, use the final_answer tool."""

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": message}
        ]
        
        response = await self.service.completion(
            model=model,
            messages=messages
        )
        
        # Parse tool usage
        lines = response.strip().split('\n')
        if len(lines) >= 2 and lines[0].startswith('TOOL:') and lines[1].startswith('INPUT:'):
            tool_name = lines[0].replace('TOOL:', '').strip()
            tool_input = lines[1].replace('INPUT:', '').strip()
            
            # Find and execute the appropriate tool
            for tool in self.tools:
                if tool.name == tool_name:
                    result = await tool.run(tool_input)
                    self.logger.log_output(result)
                    return result
        
        # If no tool format is found, return the raw response
        self.logger.log_output(response)
        return response
