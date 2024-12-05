import os
from typing import List, Dict, Any
import uuid
from services.openai_service import OpenAIService
from services.database_service import DatabaseService
from services.langfuse_service import LangFuseService
from services.types import State

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

    async def run(self, conversation_id: str, messages: List[Dict[str, str]], parent_trace=None) -> str:
        """
        Process a single conversation turn
        
        Args:
            conversation_id: UUID of the conversation
            messages: List of message dictionaries with role and content
            
        Returns:
            AI response as string
        """
        

        try:
            # Create generation observation under the main trace
            generation = parent_trace.generation(
                name="chat_response",
                model="gpt-4o-mini",  # or whatever model you're using
                input=messages,
                metadata={
                    "conversation_id": conversation_id
                }
            )
            
            # Get AI response
            ai_response = await self.openai_service.completion(messages=messages, model="gpt-4o-mini")
            
            # Store AI response
            self.db_service.store_message(conversation_id, "assistant", ai_response)
            
            # Update generation with the response and usage
            generation.end(
                output=ai_response,
                # Add usage if available from OpenAI response
                # usage={
                #     "promptTokens": response.usage.prompt_tokens,
                #     "completionTokens": response.usage.completion_tokens,
                #     "totalTokens": response.usage.total_tokens
                # }
            )
            
            return ai_response
            
        except Exception as e:
            raise Exception(f"Error in agent service: {str(e)}")
        

