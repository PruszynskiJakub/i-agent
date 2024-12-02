import asyncio
import os
import logging
from dotenv import load_dotenv
from services.openai_service import OpenAIService
from services.agent import Agent

async def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize OpenAI service with API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logging.error("Please set OPENAI_API_KEY environment variable")
        return
        
    service = OpenAIService(api_key)
    agent = Agent(service)
    
    try:
        response = await agent.run("Say hello in a creative way")
        logging.info(response)
    except Exception as e:
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

