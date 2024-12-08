import json
import os
from typing import List, Dict, Any
import uuid
from modules.openai_service import OpenAIService
from modules.database_service import DatabaseService
from modules.langfuse_service import LangfuseService
from modules.types import State

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
            system_prompt = prompt.compile()
            
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
            except:
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

    async def _execute(self, plan: str) -> str:
        """
        Execute the planned action
        
        Args:
            plan: The planned action from the AI
            parent_trace: Parent trace for logging
            
        Returns:
            Result of the execution
        """
        # For now, return the plan directly
        # This will be enhanced later to actually execute tools
        return plan

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

