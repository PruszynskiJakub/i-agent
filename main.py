import asyncio
import os
from dotenv import load_dotenv
from services.openai_service import OpenAIService

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize OpenAI service with API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
        
    service = OpenAIService(api_key)
    
    # Example message
    messages = [
        {"role": "user", "content": "Say hello in a creative way"}
    ]
    
    try:
        response = await service.completion(
            model="gpt-3.5-turbo",
            messages=messages
        )
        print(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

