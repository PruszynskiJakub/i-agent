import asyncio
import os
import uuid
import argparse
from datetime import datetime
from dotenv import load_dotenv
from modules.database_service import DatabaseService
from modules.openai_service import OpenAIService
from modules.langfuse_service import LangFuseService
from modules.agent_service import AgentService
from modules.logging_service import logger
from modules.types import State

# Load environment variables from .env file
load_dotenv()

# Initialize modules
openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))
db_service = DatabaseService()
langfuse_service = LangFuseService(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Initialize state and agent service
state = State(tools=[])  # Initialize with empty tools list
agent_service = AgentService(state, openai_service, db_service, langfuse_service)

def restore_conversation(conversation_uuid: str) -> list:
    """
    Restore conversation history from database for a given UUID
    
    Args:
        conversation_uuid: UUID of the conversation to restore
        
    Returns:
        List of message dictionaries with role and content
    """
    conversation_history = []
    stored_messages = db_service.get_messages(conversation_uuid)
    conversation_history = [{"role": msg["role"], "content": msg["content"]} for msg in stored_messages]

    if conversation_history:
        logger.info("Continuing existing conversation...")
        logger.info("\nPrevious messages in this conversation:")
        for msg in conversation_history:
            prefix = "You:" if msg["role"] == "user" else "AI:"
            print(f"\n{prefix} {msg['content']}")
        print("\n" + "-" * 50)
    
    return conversation_history

async def main_loop(conversation_uuid: str, conversation_history: list, trace, exit_keyword: str = 'exit') -> None:
    """
    Main conversation loop handling user input and AI responses
    
    Args:
        conversation_uuid: UUID of the conversation
        conversation_history: List of previous messages
        exit_keyword: Keyword to exit the conversation (default: 'exit')
    """
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check if user wants to quit
        if user_input.lower() in [exit_keyword]:
            break
        
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        try:
            # Store user message
            db_service.store_message(conversation_uuid, "user", user_input)
            
            # Get AI response using AgentService
            ai_response = await agent_service.run(conversation_uuid, conversation_history, trace)
            
            # Add AI response to conversation history
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Print AI response
            print("\nAI:", ai_response)
            
        except Exception as e:
            logger.error(f"\nError: {str(e)}")
            logger.warning("Please try again.")

async def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='AI Chat Interface')
    parser.add_argument('--conversation', type=str, help='UUID of existing conversation to continue')
    args = parser.parse_args()
    
    # Use provided UUID or generate new one
    conversation_uuid = args.conversation if args.conversation else str(uuid.uuid4())
    
    # Initialize conversation history
    conversation_history = restore_conversation(conversation_uuid) if args.conversation else []
    
    # Create a trace for the entire conversation
    trace = langfuse_service.create_trace({
        "name": "chat_conversation",
        "userid": os.getenv("USER", "default_user"),
        "sessionid": conversation_uuid,
        "tags": ["production"]
    })
    
    logger.info("Welcome to the AI Chat! (Type 'exit' to end)")
    print(f"\nConversation ID: {conversation_uuid}")
    print("-" * 50)

    await main_loop(conversation_uuid, conversation_history, trace)
    
    # End the trace when conversation is finished
    langfuse_service.finalize_trace(trace)
    langfuse_service.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
