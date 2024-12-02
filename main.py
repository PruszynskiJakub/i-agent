import asyncio
import os
from dotenv import load_dotenv
from services.openai_service import OpenAIService
from services.agent import Agent
from services.tools.final_answer import FinalAnswerTool
from services.logging_service import setup_logging, log_error, log_info

async def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize OpenAI service with API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        log_error("Please set OPENAI_API_KEY environment variable")
        return
        
    # Define tools to use
    
    service = OpenAIService(api_key)
    tools = [
        FinalAnswerTool(service)
    ]
    agent = Agent(service, tools=tools)
    
    try:
        log_info(" Starting agent...", style="bold blue")
        await agent.run("Say hello in a creative way")
        log_info("✨ Agent completed successfully", style="bold green")
    except Exception as e:
        log_error(f"Agent execution failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

