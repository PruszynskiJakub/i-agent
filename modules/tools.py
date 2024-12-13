import os
from typing import Dict, Any, List
from modules.types import Tool, WebContent
from modules.web_service import WebService
from uuid import uuid4

def get_available_tools() -> List[Tool]:
    """
    Returns a list of all available tools
    
    Returns:
        List[Tool]: List of available tools
    """
    return [
        Tool(
            uuid=uuid4(),
            name="webscrape",
            description="Scrapes content from a webpage",
            instructions="Input should be a dictionary containing 'url' key with a valid URL value, and optional 'format' key with value 'md' or 'html' (defaults to 'md').",
            function=webscrape_tool,
            required_params={"url": "The URL to scrape"},
            optional_params={"format": "Output format ('md' or 'html', defaults to 'md')"}
        )
    ]

# Initialize WebService with API key
web_service = WebService(api_key=os.getenv("FIRECRAWL_API_KEY"))

async def webscrape_tool(params: Dict[str, Any]) -> WebContent:
    """Wrapper for WebService.scrape_url"""
    return await web_service.scrape_url(params)
