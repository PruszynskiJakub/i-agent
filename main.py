import asyncio
import os
from dotenv import load_dotenv
from services.openai_service import OpenAIService
from services.agent import Agent

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize OpenAI service with API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
        
    service = OpenAIService(api_key)
    agent = Agent(service)
    
    try:
        response = await agent.run("Say hello in a creative way")
        print(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

