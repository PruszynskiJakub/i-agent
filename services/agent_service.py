from typing import List, Dict, Any
from services.openai_service import OpenAIService
from services.database_service import DatabaseService
from services.langfuse_service import LangFuseService

class AgentService:
    def __init__(self, openai_service: OpenAIService, db_service: DatabaseService, langfuse_service: LangFuseService):
        """
        Initialize AgentService
        
        Args:
            openai_service: OpenAI service instance
            db_service: Database service instance
            langfuse_service: LangFuse service instance
        """
        self.openai_service = openai_service
        self.db_service = db_service
        self.langfuse_service = langfuse_service

    async def run(self, conversation_id: str, messages: List[Dict[str, str]]) -> str:
        """
        Process a single conversation turn
        
        Args:
            conversation_id: UUID of the conversation
            messages: List of message dictionaries with role and content
            
        Returns:
            AI response as string
        """
        try:
            # Get AI response using OpenAI service
            ai_response = await self.openai_service.completion(
                messages=messages
            )
            
            # Store AI response
            self.db_service.store_message(conversation_id, "assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            raise Exception(f"Error in agent service: {str(e)}")
