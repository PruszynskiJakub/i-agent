import asyncio
import os
from datetime import datetime
from langsmith import traceable
from openai import AsyncOpenAI
from dotenv import load_dotenv
from services.database_service import DatabaseService

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI()

@traceable
async def main():
    # Initialize database service
    db_service = DatabaseService()
    
    # Initialize conversation history
    conversation_history = []
    
    print("Welcome to the AI Chat! (Type 'quit' to exit)")
    print("-" * 50)

    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check if user wants to quit
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\nAI: Goodbye! Thanks for chatting!")
            break
        
        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": user_input})
        
        try:
            # Store user message
            db_service.store_message("user", user_input)
            
            # Get AI response
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation_history,
            )
            
            # Extract AI response
            ai_response = response.choices[0].message.content
            
            # Add AI response to conversation history
            conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Store AI response
            db_service.store_message("assistant", ai_response)
            
            # Print AI response
            print("\nAI:", ai_response)
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
