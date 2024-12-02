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
        
    async def run(self, message: str) -> str:
        """
        Run the agent with an initial message
        
        Args:
            message: Initial message to send
            
        Returns:
            Model response as string
        """
        self.logger.log_input(message)
        
        response = await self.plan(message)
        result = await self.execute(response)
        
        self.logger.log_output(result)
        return result

    async def plan(self, message: str) -> str:
        """
        Create system message and get initial response from LLM
        
        Args:
            message: User message to process
            
        Returns:
            LLM response containing tool selection and parameters
        """
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
        
        return await self.service.completion(messages=messages)

    async def execute(self, response: str) -> str:
        """
        Execute the appropriate tool based on the response
        
        Args:
            response: Response from the LLM
            
        Returns:
            Result from tool execution or raw response if no tool format is found
        """
        try:
            response_json = json.loads(response)
            tool_name = response_json.get("tool")
            tool_params = response_json.get("params", {})
            
            # Find and execute the appropriate tool
            for tool in self.tools:
                if tool.name == tool_name:
                    return await tool.run(tool_params)
                    
        except json.JSONDecodeError:
            pass  # Handle the case where the response is not valid JSON
            
        # If no tool format is found, return the raw response
        return response
