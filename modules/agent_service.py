import os
from typing import List, Dict, Any
import uuid
from modules.openai_service import OpenAIService
from modules.database_service import DatabaseService
from modules.langfuse_service import LangFuseService
from modules.types import State

class AgentService:
    def __init__(self, state: State, openai_service: OpenAIService, db_service: DatabaseService, langfuse_service: LangFuseService):
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

    async def _execute(self, plan: str, conversation_id: str, parent_trace=None) -> str:
        """
        Execute the planned action
        
        Args:
            plan: The planned action from the AI
            conversation_id: UUID of the conversation
            parent_trace: Parent trace for logging
            
        Returns:
            Result of the execution
        """
        # For now, return the plan directly
        # This will be enhanced later to actually execute tools
        return plan

    async def _plan(self, conversation_id: str, messages: List[Dict[str, str]], parent_trace=None) -> tuple[str, bool]:
        """
        Plan and execute the next conversation turn
        
        Args:
            conversation_id: UUID of the conversation
            messages: List of message dictionaries with role and content
            parent_trace: Parent trace for logging
            
        Returns:
            AI response as string
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
                    "conversation_id": conversation_id
                }
            )
            
            # Get AI response
            ai_response = await self.openai_service.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                model=model
            )
            
            # Store AI response
            self.db_service.store_message(conversation_id, "assistant", ai_response)
            
            # Update generation with the response
            generation.end(
                output=ai_response,
            )
            
            # Check if this is a final answer
            is_final = "final_answer" in ai_response.lower()
            
            return ai_response, is_final
            
        except Exception as e:
            raise Exception(f"Error in agent service: {str(e)}")

    async def run(self, conversation_id: str, messages: List[Dict[str, str]], parent_trace=None) -> str:
        """
        Process conversation turns with planning and execution loop
        
        Args:
            conversation_id: UUID of the conversation
            messages: List of message dictionaries with role and content
            parent_trace: Parent trace for logging
            
        Returns:
            Final AI response as string
        """
        max_iterations = 5
        iteration = 0
        
        while iteration < max_iterations:
            # Increment iteration counter
            iteration += 1
            
            # Plan phase
            plan, is_final = await self._plan(conversation_id, messages, parent_trace)
            
            # If this is a final answer, return it
            if is_final:
                return plan
                
            # Execute phase
            result = await self._execute(plan, conversation_id, parent_trace)
            
            # Add the result to messages for next iteration
            messages.append({"role": "assistant", "content": result})
            
        # If we hit max iterations, return the last result
        return result

