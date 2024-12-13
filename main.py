import argparse
import asyncio
import os
import uuid

from dotenv import load_dotenv

from modules.agent_service import AgentService
from modules.database_service import DatabaseService
from modules.langfuse_service import LangfuseService
from modules.logging_service import logger
from modules.openai_service import OpenAIService
from modules.web_service import WebService
from modules.text_service import TextService
from modules.types import State, Tool

# Load environment variables from .env file
load_dotenv()

# Initialize modules
openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))
db_service = DatabaseService()
langfuse_service = LangfuseService(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)
text_service = TextService()
web_service = WebService(
    api_key=os.getenv("FIRECRAWL_API_KEY"),
    text_service=text_service,
    db_service=db_service
)


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


async def main_loop(conversation_uuid: str, conversation_history: list, exit_keyword: str = 'exit') -> None:
    """
    Main conversation loop handling user input and AI responses
    
    Args:
        conversation_uuid: UUID of the conversation
        conversation_history: List of previous messages
        exit_keyword: Keyword to exit the conversation (default: 'exit')
    """
    # Initialize state and agent service
    state = State(
        conversation_uuid=conversation_uuid,
        tools=[
            Tool(
                uuid=uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
                name="webscrape",
                description="Scrapes content from a webpage",
                instructions="Input should be a dictionary containing 'url' key with a valid URL value, and optional 'format' key with value 'md' or 'html' (defaults to 'md').",
                required_params={"url": "The URL to scrape"},
                optional_params={"format": "Output format ('md' or 'html', defaults to 'md')"}
            )
        ]
    )
    agent_service = AgentService(state, openai_service, db_service, langfuse_service, web_service)

    while True:
        # Get user input
        user_input = input("\nYou: ").strip()

        # Create a trace for this interaction
        trace = langfuse_service.create_trace({
            "name": user_input[:45],  # First 45 chars of user input as trace name
            "userid": os.getenv("USER", "default_user"),
            "sessionid": conversation_uuid,
            "tags": ["production"]
        })

        # Check if user wants to quit
        if user_input.lower() in [exit_keyword]:
            break

        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        try:
            # Get AI response using AgentService
            state.conversation_uuid = conversation_uuid
            ai_response = await agent_service.run(conversation_history, trace)

            # Add AI response to conversation history
            conversation_history.append({"role": "assistant", "content": ai_response})

            # Print AI response
            print("\nAI:", ai_response)

            # Finalize the trace with input and output
            langfuse_service.finalize_trace(
                trace,
                input=conversation_history[:-1],  # All messages except the last AI response
                output=ai_response
            )

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

    logger.info("Welcome to the AI Chat! (Type 'exit' to end)")
    print(f"\nConversation ID: {conversation_uuid}")
    print("-" * 50)

    await main_loop(conversation_uuid, conversation_history)

    # Shutdown langfuse client
    langfuse_service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
