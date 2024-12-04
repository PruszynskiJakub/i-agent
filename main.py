import asyncio
import os
import uuid
import argparse
from datetime import datetime
from dotenv import load_dotenv
from services.database_service import DatabaseService
from services.openai_service import OpenAIService
from services.langfuse_service import LangFuseService
from services.agent_service import AgentService

# Load environment variables from .env file
load_dotenv()

# Initialize services
openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))
db_service = DatabaseService()
langfuse_service = LangFuseService(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Initialize agent service
agent_service = AgentService(openai_service, db_service, langfuse_service)

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
        print("Continuing existing conversation...")
        print("\nPrevious messages in this conversation:")
        for msg in conversation_history:
            prefix = "You:" if msg["role"] == "user" else "AI:"
            print(f"\n{prefix} {msg['content']}")
        print("\n" + "-" * 50)
    
    return conversation_history

async def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='AI Chat Interface')
    parser.add_argument('--conversation', type=str, help='UUID of existing conversation to continue')
    args = parser.parse_args()
    
    # Use provided UUID or generate new one
    conversation_uuid = args.conversation if args.conversation else str(uuid.uuid4())
    
    # Initialize conversation history
    conversation_history = restore_conversation(conversation_uuid) if args.conversation else []
    
    # Start tracing the conversation with LangFuse
    trace = langfuse_service.create_trace({
        "id": str(uuid.uuid4()),
        "name": "chat_conversation",
        "userid": os.getenv("USER", "default_user"),
        "sessionid": conversation_uuid
    })
    
    print("Welcome to the AI Chat! (Type 'quit' to exit)")
    print(f"\nConversation ID: {conversation_uuid}")
    print("-" * 50)

    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check if user wants to quit
        if user_input.lower() in ['exit']:
            break
        
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        try:
            # Store user message
            db_service.store_message(conversation_uuid, "user", user_input)
            
            # Get AI response using AgentService
            ai_response = await agent_service.run(conversation_uuid, conversation_history)
            
            # Add AI response to conversation history
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Print AI response
            print("\nAI:", ai_response)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")
    
    # End the trace when conversation is finished
    langfuse_service.end_trace(trace)

if __name__ == "__main__":
    asyncio.run(main())
