from typing import List, Dict, Any
from services.openai_service import OpenAIService
from services.logging_service import log_info, log_error, log_tool_call, log_warning
from services.prompts.plan import plan_prompt
from services.tools.final_answer import FinalAnswerTool
from services.utils import format_tools_for_prompt
import json

class Agent:
    def __init__(self, service: OpenAIService, tools: List = None):
        self.service = service
        self.tools = tools
        self.tools_mapping = {tool.name: tool for tool in self.tools}
        
    async def run(self, message: str) -> str:
        log_info(f"⬆️ User Input: {message}", style="bold blue")
        
        try:
            response = await self.plan(message)
            result = await self.execute(response)
            
            log_info(f"⬇️ Final Output: {result}", style="bold green")
            return result
            
        except Exception as e:
            log_error(f"Error during agent execution: {str(e)}")
            raise

    async def plan(self, message: str) -> Dict[str, any]:
        messages = [
            {"role": "system", "content": plan_prompt({"tools": self.tools_mapping})},
            {"role": "user", "content": message}
        ]
        
        log_info(" Planning response...", style="bold yellow")
        response = await self.service.completion(messages=messages, json_mode=True)
        log_info(f"📝 Plan created: {response}", style="bold cyan")
        return json.loads(response)
    
    async def execute(self, next_step: Dict[str, any]) -> dict[str, Any] | Any:
        try:
            tool_name = next_step.get("tool_name")
            tool_params = next_step.get("parameters", {})
            
            # Find and execute the appropriate tool
            for tool in self.tools:
                if tool.name == tool_name:
                    result = await tool.execute(tool_params)
                    log_tool_call(tool_name, tool_params, result)
                    return result
                    
        except json.JSONDecodeError:
            log_warning("Response was not in JSON format, returning raw response")
            return next_step
            
        except Exception as e:
            log_error(f"Error executing tool: {e}")
            raise
            
        # If no tool format is found, return the raw response
        return next_step
