from typing import List, Dict
from services.openai_service import OpenAIService
from services.logging_service import LoggingService
from services.tools.final_answer import FinalAnswerTool
import json

class Agent:
    def __init__(self, service: OpenAIService, tools: List = None):
        self.service = service
        self.logger = LoggingService()
        self.tools = tools or [FinalAnswerTool()]
        
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

        To use a tool, respond with a JSON object:
        {{
            "tool": "<tool_name>",
            "params": {{}}
        }}

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
        try:
            response_json = json.loads(response)
            tool_name = response_json.get("tool")
            tool_params = response_json.get("params", {})
            
            # Find and execute the appropriate tool
            for tool in self.tools:
                if tool.name == tool_name:
                    result = await tool.run(tool_params)
                    self.logger.log_output(result)
                    return result
        except json.JSONDecodeError:
            pass  # Handle the case where the response is not valid JSON

        # If no tool format is found, return the raw response
        self.logger.log_output(response)
        return response
