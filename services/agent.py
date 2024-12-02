from typing import List, Dict, Any
from services.openai_service import OpenAIService
from services.logging_service import log_info, log_error, log_tool_call, log_warning
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
        formatted_tools = format_tools_for_prompt(self.tools_mapping)

        system_message = f"""Given the task description, current context, and key findings, determine the SINGLE NEXT STEP to take.
        
        Available tools:
        {formatted_tools}
       
        <rules>
        1. Plan only ONE next step that brings us closer to completing the task
        2. Keep any placeholders in the format [[PLACEHOLDER_NAME]]
        3. Consider the context history to avoid redundant operations
        4. Use ONLY the tools and parameters listed in the 'Available tools' section
        5. Base your decision on factual information from the key findings and context
        6. Do not introduce any information or assumptions not present in the provided data
        </rules>
        
        Respond in the following JSON format:
        {{
            "_thinking": "Explain why this specific step is the best next action, referencing key findings or context",
             "step": "description of the single next step",
            "tool_name": "exact name of the tool to use from the available tools",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}"""

        messages = [
            {"role": "system", "content": system_message},
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
            log_error(f"Error executing tool: {str(e)}")
            raise
            
        # If no tool format is found, return the raw response
        return next_step
