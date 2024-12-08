import json
import os
from typing import List, Dict, Any
import uuid
from modules.logging_service import log_info, log_error, log_tool_call
from modules.openai_service import OpenAIService
from modules.database_service import DatabaseService
from modules.langfuse_service import LangfuseService
from modules.types import State
from modules.utils import format_tools_for_prompt

class AgentService:
    def __init__(self, state: State, openai_service: OpenAIService, db_service: DatabaseService, langfuse_service: LangfuseService):
        """
        Initialize AgentService
        
        Args:
            state: State instance containing tools and other configuration
            openai_service: OpenAI service instance
            db_service: Database service instance
            langfuse_service: LangFuse service instance
        """
        self.state = state
        self.openai_service = openai_service
        self.db_service = db_service
        self.langfuse_service = langfuse_service

    async def run(self, messages: List[Dict[str, Any]], parent_trace=None) -> str:
        """
        Process conversation turns with planning and execution loop
        
        Args:
            messages: List of message dictionaries with role and content
            parent_trace: Parent trace for logging
            
        Returns:
            Final AI response as string
        """
        self.db_service.store_message(self.state.conversation_uuid, "user", messages[-1]['content'])

        while self.state.config["current_step"] < self.state.config["max_steps"]:
            # Plan phase
            plan_result = await self._plan(messages, parent_trace)
            
            # If the tool is final_answer, return empty string
            if plan_result["tool"] == "final_answer":
                break
                
            # Execute phase
            result = await self._execute(plan_result)
            
            # Add the result to messages for next iteration
            messages.append({"role": "assistant", "content": result})
            
            # Increment step counter at end of loop
            self.state.config["current_step"] += 1
            
        # Get final answer using answer method
        final_answer = await self.answer(messages, parent_trace)

        self.db_service.store_message(self.state.conversation_uuid, "assistant", final_answer)
        
        return final_answer

    async def _plan(self, messages: List[Dict[str, Any]], parent_trace=None) -> Dict[str, Any]:
        """
        Plan and execute the next conversation turn
        
        Args:
            messages: List of message dictionaries with role and content
            parent_trace: Parent trace for logging
            
        Returns:
            Dictionary containing the AI response and tool information
        """
        try:
            # Get system prompt
            prompt = self.langfuse_service.get_prompt(
                name="agent_plan",
                prompt_type="text",
                label="latest"
            )
            
            # Compile the prompt with any needed variables
            system_prompt = prompt.compile(
                formatted_tools=format_tools_for_prompt(self.state.tools)
            )
            
            # Get model from prompt config, fallback to default if not specified
            model = prompt.config.get("model", "gpt-4o-mini")
            
            # Create generation observation under the main trace
            generation = parent_trace.generation(
                name="agent_plan",
                model=model,  # Use model from prompt config
                input=messages,
                metadata={
                    "conversation_id": self.state.conversation_uuid
                }
            )
            
            # Get AI response with JSON mode enabled
            completion = await self.openai_service.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                model=model,
                json_mode=True
            )
            
            # Parse the response as JSON
            try:
                response_data = json.loads(completion)
                log_info(f"Plan generated: {response_data}", style="bold blue")
            except json.JSONDecodeError as e:
                log_error(f"Failed to parse JSON response: {str(e)}")
                response_data = {}
            
            # Store AI response
            self.db_service.store_message(self.state.conversation_uuid, "assistant", completion)
            
            # Update generation with the response
            generation.end(
                output=response_data,
            )

            ## To Remove
            response_data['tool'] = response_data.get('tool', 'final_answer')

            return response_data
            
        except Exception as e:
            raise Exception(f"Error in agent service: {str(e)}")

    async def _execute(self, plan: Dict[str, Any]) -> str:
        """
        Execute the planned action using the specified tool
        
        Args:
            plan: Dictionary containing the plan details including tool name and parameters
            
        Returns:
            Result of the tool execution
        """
        log_info(f"Executing plan with tool: {plan.get('tool', 'unknown')}", style="bold cyan")
        
        # Validate plan structure
        required_fields = ["_thinking", "step", "tool", "parameters", "required_information"]
        if not all(field in plan for field in required_fields):
            error_msg = f"Plan missing required fields. Must include: {required_fields}"
            log_error(error_msg)
            raise ValueError(error_msg)
            
        # Find matching tool
        tool = next((t for t in self.state.tools if t.name == plan["tool"]), None)
        if not tool:
            error_msg = f"Tool '{plan['tool']}' not found in available tools"
            log_error(error_msg)
            raise ValueError(error_msg)
            
        # Validate required parameters
        missing_params = [param for param in tool.required_params if param not in plan["parameters"]]
        if missing_params:
            raise ValueError(f"Missing required parameters for tool '{tool.name}': {missing_params}")
            
        try:
            # Execute the tool with parameters
            log_info(f"Executing {tool.name} with parameters: {plan['parameters']}", style="bold magenta")
            result = await tool.function(plan["parameters"])
            log_tool_call(tool.name, plan["parameters"], result)
            return result
            
        except Exception as e:
            error_msg = f"Error executing tool '{tool.name}': {str(e)}"
            log_error(error_msg)
            raise Exception(error_msg)

    async def answer(self, messages: List[Dict[str, Any]], parent_trace=None) -> str:
        """
        Generate a final answer to the user
        
        Args:
            messages: List of message dictionaries with role and content
            parent_trace: Parent trace for logging
            
        Returns:
            Final answer as string
        """
        try:
            # Get system prompt for final answer
            prompt = self.langfuse_service.get_prompt(
                name="agent_answer",
                prompt_type="text",
                label="latest"
            )
            
            # Compile the prompt
            system_prompt = prompt.compile()
            
            # Get model from prompt config, fallback to default
            model = prompt.config.get("model", "gpt-4o-mini")
            
            # Create generation observation
            generation = parent_trace.generation(
                name="agent_answer",
                model=model,
                input=messages,
                metadata={
                    "conversation_id": self.state.conversation_uuid
                }
            )
            
            # Get final answer from OpenAI
            final_answer = await self.openai_service.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                model=model
            )
                        
            # Update generation with the response
            generation.end(
                output=final_answer,
            )
            
            return final_answer
            
        except Exception as e:
            raise Exception(f"Error generating final answer: {str(e)}")

