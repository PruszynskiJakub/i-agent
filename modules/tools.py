import os
from typing import Dict, Any, List
from firecrawl import FirecrawlApp
from modules.logging_service import log_tool_call
from modules.types import Tool, WebContent

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

async def webscrape_tool(params: Dict[str, Any]) -> WebContent:
    """
    Scrapes content from a given URL in specified format
    
    Args:
        params: Dictionary containing:
            - url: The URL to scrape
            - format: Format to return ('md' or 'html')
        
    Returns:
        WebContent object containing:
            - url: The scraped URL
            - content: scraped content in requested format
            - type: format type ('md' or 'html')
    """
    url = params.get('url')
    format_type = params.get('format', 'md')  # Default to markdown
    
    if not url:
        raise ValueError("URL parameter is required")
        
    if format_type not in ['md', 'html']:
        raise ValueError("Format must be 'md' or 'html'")
        
    try:
        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
        formats = ['markdown'] if format_type == 'md' else ['html']
        
        data = app.scrape_url(url, params={'formats': formats})
        
        content = data.get('markdown' if format_type == 'md' else 'html', '')
        
        web_content = WebContent(
            url=url,
            content=content,
            type=format_type
        )
        
        log_tool_call("webscrape_tool", params, {"status": "success", "content_length": len(content)})
        return web_content
        
    except Exception as e:
        log_tool_call("webscrape_tool", params, {"error": str(e)})
        raise
