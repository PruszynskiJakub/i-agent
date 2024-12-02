from typing import List, Dict
from services.openai_service import OpenAIService
from services.logging_service import log_info, log_error, log_tool_call
from services.tools.final_answer import FinalAnswerTool
import json

class Agent:
    def __init__(self, service: OpenAIService, tools: List = None):
        self.service = service
        self.tools = tools or [FinalAnswerTool()]
        
    async def run(self, message: str) -> str:
        """
        Run the agent with an initial message
        
        Args:
            message: Initial message to send
            
        Returns:
            Model response as string
        """
        log_info(f"⬆️ User Input: {message}", style="bold blue")
        
        try:
            response = await self.plan(message)
            result = await self.execute(response)
            
            log_info(f"⬇️ Final Output: {result}", style="bold green")
            return result
            
        except Exception as e:
            log_error(f"Error during agent execution: {str(e)}")
            raise

    async def plan(self, message: str) -> str:
        """
        Create system message and get initial response from LLM
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
        
        log_info(" Planning response...", style="bold yellow")
        response = await self.service.completion(messages=messages)
        log_info(f"📝 Plan created: {response}", style="bold cyan")
        return response

    async def execute(self, response: str) -> str:
        """
        Execute the appropriate tool based on the response
        """
        try:
            response_json = json.loads(response)
            tool_name = response_json.get("tool")
            tool_params = response_json.get("params", {})
            
            # Find and execute the appropriate tool
            for tool in self.tools:
                if tool.name == tool_name:
                    result = await tool.run(tool_params)
                    log_tool_call(tool_name, tool_params, result)
                    return result
                    
        except json.JSONDecodeError:
            log_warning("Response was not in JSON format, returning raw response")
            return response
            
        except Exception as e:
            log_error(f"Error executing tool: {str(e)}")
            raise
            
        # If no tool format is found, return the raw response
        return response
