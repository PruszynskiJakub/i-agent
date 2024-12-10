import os
from typing import Dict, Any, Literal, List
from firecrawl import FirecrawlApp
from modules.logging_service import log_tool_call
from modules.types import Tool

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

def webscrape_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scrapes content from a given URL in specified format
    
    Args:
        params: Dictionary containing:
            - url: The URL to scrape
            - format: Format to return ('md' or 'html')
        
    Returns:
        Dict containing:
            - content: scraped content in requested format
            - metadata: page metadata
            - status: HTTP status code
    """
    url = params.get('url')
    format_type = params.get('format', 'md')  # Default to markdown
    
    if not url:
        return {"error": "URL parameter is required", "status": 400}
        
    if format_type not in ['md', 'html']:
        return {"error": "Format must be 'md' or 'html'", "status": 400}
        
    try:
        app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))  # Replace with env variable
        formats = ['markdown'] if format_type == 'md' else ['html']
        
        result = app.scrape_url(url, params={'formats': formats})
        
        if not result or 'data' not in result:
            error_result = {
                "error": "Failed to scrape page",
                "status": 500
            }
            log_tool_call("webscrape_tool", params, error_result)
            return error_result
            
        content = result['data'].get('markdown' if format_type == 'md' else 'html', '')
        metadata = result['data'].get('metadata', {})
        
        success_result = {
            "content": content,
            "metadata": metadata,
            "status": metadata.get('statusCode', 200)
        }
        log_tool_call("webscrape_tool", params, success_result)
        return success_result
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "status": 500
        }
        log_tool_call("webscrape_tool", params, error_result)
        return error_result
